from datetime import datetime


from typing import (
    List,
    Optional
)


from pydantic import (
    BaseModel
)





class RiskDistributionSchema(
    BaseModel
):

    """
    Risk severity distribution.
    Used for pie/bar charts.
    """



    critical: int = 0



    high: int = 0



    medium: int = 0



    low: int = 0





class RiskTrendPointSchema(
    BaseModel
):

    """
    Risk trend chart point.
    """



    date: str



    score: float



    level: str





class RiskCommitSchema(
    BaseModel
):

    """
    Top risky commit information.
    """



    commit_id: str



    risk_score: float



    risk_level: str



    blocked: bool





class RepositoryRiskSchema(
    BaseModel
):

    """
    Repository risk ranking.
    """



    repository: str



    average_risk: float





class SecuritySummarySchema(
    BaseModel
):

    """
    Security posture summary.
    """



    total_security_findings: int



    critical_security_findings: int





class DashboardOverviewSchema(
    BaseModel
):

    """
    Dashboard overview metrics.
    """



    total_commits: int



    total_analysis: int



    blocked_deployments: int



    risk_distribution: RiskDistributionSchema





class DashboardResponseSchema(
    BaseModel
):

    """
    Complete dashboard response.
    """



    overview: DashboardOverviewSchema



    risky_commits: List[
        RiskCommitSchema
    ] = []



    security_summary: SecuritySummarySchema



    risk_trends: List[
        RiskTrendPointSchema
    ] = []



    repositories: List[
        RepositoryRiskSchema
    ] = []



    security_score: float



    generated_at: datetime





    class Config:

        from_attributes = True