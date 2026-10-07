import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, UUID, ForeignKey, Enum, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin, Base

class WorkspaceRole(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"

class Workspace(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[str] = mapped_column(UUID(as_uuid=True),ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    members: Mapped[list["WorkspaceMember"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    workspace_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(Enum(WorkspaceRole, name="workspace_role"), default=WorkspaceRole.MEMBER, nullable=False)
    joined_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    workspace: Mapped["Workspace"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()