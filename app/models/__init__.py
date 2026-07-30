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



__all__ = [

    "Commit",

    "FileChange",

    "RuleResult",

    "RiskAnalysis"

]