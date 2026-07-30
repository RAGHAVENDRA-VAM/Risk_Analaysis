from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    event_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    action: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    entity_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    entity_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    user_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    correlation_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="Success"
    )

    http_status_code: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    is_error: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog("
            f"event='{self.event_type}', "
            f"status='{self.status}'"
            f")>"
        )