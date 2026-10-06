import uuid
from typing import Annotated

from fastapi import Depends, Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotAuthenticatedException, ResourceNotFoundException, PermissionDeniedException
from app.core.security import decode_access_token
from app.models.user import User
from app.models.wokspace import WorkspaceRole, WorkspaceMember

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(db: Annotated[AsyncSession, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise NotAuthenticatedException()

    user_id_str: str | None = payload.get("sub")
    if not user_id_str:
        raise NotAuthenticatedException()

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise NotAuthenticatedException()

    query = select(User).where(User.id == user_uuid)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise NotAuthenticatedException()

    return user

class RequireWorkspaceRole:
    def __init__(self, allowed_roles: list[WorkspaceRole]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(self, workspace_id: Annotated[uuid.UUID, Path(...)], current_user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]) -> WorkspaceMember:
        query = select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == current_user.id)
        result = await db.execute(query)
        membership = result.scalar_one_or_none()

        if membership is None:
            raise ResourceNotFoundException("Workspace")

        if membership.role not in self.allowed_roles:
            raise PermissionDeniedException(detail=f"Action requires one of roles: {[r.value for r in self.allowed_roles]}")

        return membership