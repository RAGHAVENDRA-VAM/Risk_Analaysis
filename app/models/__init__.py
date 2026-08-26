"""
SQLAlchemy model registration.

Import all models here so that
SQLAlchemy can discover tables and
relationships during application startup.
"""

from app.models.commit import Commit
from app.models.file_change import FileChange
from app.models.rule_result import RuleResult
from app.models.risk_analysis import RiskAnalysis
from app.models.risk_finding import RiskFinding
from app.models.recommendation import Recommendation
from app.models.audit_log import AuditLog
from app.models.analysis_history import AnalysisHistory
from app.models.ai_token_usage import AITokenUsage

__all__ = [
    "Commit",
    "FileChange",
    "RuleResult",
    "RiskAnalysis",
    "RiskFinding",
    "Recommendation",
    "AuditLog",
    "AnalysisHistory",
    "AITokenUsage"
]
