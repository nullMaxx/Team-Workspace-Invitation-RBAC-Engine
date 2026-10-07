import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, RequireWorkspaceRole
from app.core.database import get_db
from app.core.exceptions import ConflictException, ResourceNotFoundException
from app.models import workspace
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole
from app.schemas.workspace import WorkspaceResponse, WorkspaceCreate, WorkspaceMemberResponse, WorkspaceMemberRoleUpdate

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED, summary="Create a new workspace")
async def create_workspace(payload: WorkspaceCreate, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]) -> Workspace:
    workspace = Workspace(name=payload.name, owner_id=current_user.id)
    db.add(workspace)
    await db.flush()

    owner_membership = WorkspaceMember(workspace_id=workspace.id, user_id=current_user.id, role=WorkspaceRole.OWNER)
    db.add(owner_membership)

    await db.commit()
    await db.refresh(workspace)
    return workspace

@router.post("/{workspace_id}/members", response_model=list[WorkspaceMemberResponse], summary="List workspace members (Any member can view)")
async def list_members(workspace_id: uuid.UUID,
                       membership: Annotated[WorkspaceMember,
                       Depends(RequireWorkspaceRole([
                           WorkspaceRole.OWNER,
                           WorkspaceRole.ADMIN,
                           WorkspaceRole.MEMBER,
                           WorkspaceRole.VIEWER
                       ]))],
                        db: Annotated[AsyncSession, Depends(get_db)]) -> list[WorkspaceMember]:
    query = (select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id).options(selectinload(WorkspaceMember.user)))
    result = await db.execute(query)
    return list(result.scalars().all())

@router.patch("/{workspace_id}/members/{user_id}", response_model=WorkspaceMemberResponse, summary="Update member role (OWNER or ADMIN only)")
async def update_member_role(workspace_id: uuid.UUID, user_id: uuid.UUID, payload:WorkspaceMemberRoleUpdate, membership: Annotated[WorkspaceMember,
                                            Depends(RequireWorkspaceRole([WorkspaceRole.OWNER, WorkspaceRole.ADMIN]))], db: Annotated[AsyncSession, Depends(get_db)]) -> WorkspaceMember:
    if payload.role == WorkspaceRole.OWNER:
        raise ConflictException("Cannot promote to OWNER via this endpoint; use ownership transfer")

    query = (select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == user_id).options(selectinload(WorkspaceMember.user)))
    result = await db.execute(query)
    target_member = result.scalar_one_or_none()

    if target_member is None:
        raise ResourceNotFoundException("Workspace member")

    if target_member.role == WorkspaceRole.OWNER:
        raise ConflictException("Cannot change the role of the workspace owner")

    target_member.role = payload.role
    await db.commit()
    await db.refresh(target_member)
    return target_member
