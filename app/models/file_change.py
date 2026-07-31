from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FileChange(Base):
    __tablename__ = "file_changes"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    commit_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("commits.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    file_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_extension: Mapped[str] = mapped_column(
        String(25),
        nullable=False
    )

    change_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    additions: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    deletions: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    total_changes: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    is_source_code: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    is_configuration_file: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_infrastructure_file: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_security_sensitive: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    commit = relationship(
        "Commit",
        back_populates="file_changes"
    )

    rule_results = relationship(
        "RuleResult",
        back_populates="file",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<FileChange("
            f"path='{self.file_path}', "
            f"type='{self.change_type}'"
            f")>"
        )