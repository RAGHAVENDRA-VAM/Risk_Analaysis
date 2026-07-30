from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON
)

from sqlalchemy.orm import relationship

from app.core.database import Base



class RuleResult(Base):
    """
    Stores deterministic rule engine findings.
    """


    __tablename__ = "rule_results"



    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    commit_id = Column(
        String(36),
        ForeignKey(
            "commits.id"
        ),
        nullable=False
    )


    file_id = Column(
        String(36),
        ForeignKey(
            "file_changes.id"
        ),
        nullable=True
    )


    #
    # Rule Information
    #

    rule_name = Column(
        String(200),
        nullable=False
    )


    rule_category = Column(
        String(100),
        nullable=False
    )


    severity = Column(
        String(50),
        nullable=False
    )


    risk_score = Column(
        Integer,
        default=0
    )


    description = Column(
        Text,
        nullable=True
    )


    recommendation = Column(
        Text,
        nullable=True
    )


    #
    # Detection Details
    #

    findings = Column(
        JSON,
        nullable=True
    )


    matched_pattern = Column(
        String(500),
        nullable=True
    )


    is_blocking = Column(
        Boolean,
        default=False
    )


    #
    # Audit
    #

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


    #
    # Relationships
    #

    commit = relationship(
        "Commit",
        back_populates="rule_results"
    )


    file = relationship(
        "FileChange",
        back_populates="rule_results"
    )



    def to_dict(
        self
    ):

        return {

            "id":
                self.id,

            "commit_id":
                self.commit_id,

            "file_id":
                self.file_id,

            "rule_name":
                self.rule_name,

            "category":
                self.rule_category,

            "severity":
                self.severity,

            "risk_score":
                self.risk_score,

            "description":
                self.description,

            "recommendation":
                self.recommendation,

            "findings":
                self.findings,

            "matched_pattern":
                self.matched_pattern,

            "is_blocking":
                self.is_blocking,

            "created_at":
                self.created_at.isoformat()
                if self.created_at
                else None
        }