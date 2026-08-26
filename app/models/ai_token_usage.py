from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime
)
from sqlalchemy.sql import func
from app.core.database import Base

class AITokenUsage(Base):
    """
    Tracks OpenAI API token consumption and latency for each analysis.
    """
    __tablename__ = "ai_token_usage"

    id = Column(Integer, primary_key=True, index=True)
    commit_id = Column(String(200), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    latency_ms = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
