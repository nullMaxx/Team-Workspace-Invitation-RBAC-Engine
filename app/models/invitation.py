import enum
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, UUID, String, Enum, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin, Base
from app.models.wokspace import WorkspaceRole


class InvitationStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

class Invitation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "invitations"

    workspace_id: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", on_delete="CASCADE"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    role: Mapped[WorkspaceRole] = mapped_column(Enum(WorkspaceRole, name="workspace_role_enum"),default=WorkspaceRole.MEMBER, nullable=False)
    status: Mapped[InvitationStatus] = mapped_column(Enum(InvitationStatus, name="invitation_status_enum"), default=InvitationStatus.PENDING, nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    workspace: Mapped["Workspace"] = relationship()