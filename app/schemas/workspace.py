from datetime import datetime
import uuid

from pydantic import BaseModel, Field, ConfigDict

from app.models.workspace import WorkspaceRole
from app.schemas.user import UserResponse


class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Acme Corp"])

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceResponse(WorkspaceBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceMemberResponse(BaseModel):
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    role: WorkspaceRole
    joined_at: datetime
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)

class WorkspaceMemberRoleUpdate(BaseModel):
    role: WorkspaceRole