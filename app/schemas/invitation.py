from datetime import datetime
import uuid

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.invitation import InvitationStatus
from app.models.wokspace import WorkspaceRole


class InvitationCreate(BaseModel):
    email: EmailStr
    role: WorkspaceRole = Field(default=WorkspaceRole.MEMBER, description="Initial role to grant when invitation is accepted")

class InvitationResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    email: EmailStr
    role: WorkspaceRole
    status: InvitationStatus
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InvitationCreatedResponse(InvitationResponse):
    raw_token: str = Field(..., description="One-time secret token. Include this in the invitation link sent to the user")
