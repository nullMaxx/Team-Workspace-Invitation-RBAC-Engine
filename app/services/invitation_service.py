import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictException, ResourceNotFoundException
from app.core.security import generate_invitation_token, hash_token
from app.models import workspace
from app.models.invitation import Invitation, InvitationStatus
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.schemas.invitation import InvitationCreate, InvitationCreatedResponse


class InvitationService:
    @staticmethod
    async def create_invitation(db: AsyncSession, workspace_id: uuid.UUID, payload: InvitationCreate) -> InvitationCreatedResponse:
        member_check_query = (select(WorkspaceMember).join(User, WorkspaceMember.user_id == User.id).where(WorkspaceMember.workspace_id == workspace_id, User.email == payload.email))
        existing_member = (await db.execute(member_check_query)).scalar_one_or_none()
        if existing_member:
            raise ConflictException("User is already a member of this workspace")

        pending_invite_query = select(Invitation).where(Invitation.workspace_id == workspace_id, Invitation.email == payload.email, Invitation.status == InvitationStatus.PENDING)
        existing_invite = (await db.execute(pending_invite_query)).scalar_one_or_none()
        if existing_invite:
            raise ConflictException("A pending invitation already exists for this email")

        raw_token, token_hash = generate_invitation_token()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.INVITATION_TOKEN_EXPIRE_DAYS)

        invitation = Invitation(workspace_id=workspace_id, email=payload.email, role=payload.role, status=InvitationStatus.PENDING, token_hash=token_hash, expires_at=expires_at)

        db.add(invitation)
        await db.commit()
        await db.refresh(invitation)

        return InvitationCreatedResponse(id=invitation.id, workspace_id=invitation.workspace_id,
                                         email=invitation.email, role=invitation.role,
                                         status=invitation.status, expires_at=invitation.expires_at,
                                         created_at=invitation.created_at, raw_token=raw_token)

    @staticmethod
    async def accept_invitation(db: AsyncSession, raw_token: str, current_user: User) -> WorkspaceMember:
        token_hash = hash_token(raw_token)
        now = datetime.now(timezone.utc)

        query = (select(Invitation).where(Invitation.token_hash == token_hash).with_for_update())
        result = await db.execute(query)
        invitation = result.scalar_one_or_none()

        if invitation is None:
            raise ResourceNotFoundException("Invitation")

        if invitation.status != InvitationStatus.PENDING:
            raise ConflictException(f"Invitation is already {invitation.status.value.lower()}")

        if invitation.expires_at < now:
            invitation.status = InvitationStatus.EXPIRED
            await db.commit()
            raise ConflictException("Invitation has expired")

        if invitation.email.lower() != current_user.email.lower():
            raise ConflictException("This invitation was issued for a different email address")

        invitation.status = InvitationStatus.ACCEPTED

        new_member = WorkspaceMember(workspace_id=invitation.workspace_id, user_id=current_user.id, role=invitation.role)
        db.add(new_member)

        await db.commit()
        await db.refresh(new_member)
        return new_member


