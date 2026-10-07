import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RequireWorkspaceRole, get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.workspace import WorkspaceMember, WorkspaceRole
from app.schemas.invitation import InvitationCreate, InvitationCreatedResponse
from app.schemas.workspace import WorkspaceMemberResponse
from app.services.invitation_service import InvitationService

router = APIRouter(tags=["Invitations"])

@router.post("/workspaces/{workspace_id}/invitations", response_model=InvitationCreatedResponse, status_code=status.HTTP_201_CREATED, summary="Create an invitation (OWNER or ADMIN only)")
async def create_invitation(workspace_id: uuid.UUID, payload: InvitationCreate, current_user: Annotated[WorkspaceMember, Depends(RequireWorkspaceRole([WorkspaceRole.OWNER, WorkspaceRole.ADMIN]))], db: Annotated[AsyncSession, Depends(get_db)]) -> InvitationCreatedResponse:
    return await InvitationService.create_invitation(db=db, workspace_id=workspace_id, payload=payload)

@router.post("/invitations/{raw_token}/accept", response_model=WorkspaceMemberResponse, summary="Accept an invitation using the secret token")
async def accept_invitation(raw_token: str, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]) -> WorkspaceMember:
    return await InvitationService.accept_invitation(db=db, raw_token=raw_token, current_user=current_user)
