from datetime import datetime

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard_schema import (
    RiskDistributionSchema,
    RiskCommitSchema,
    RiskTrendPointSchema,
    RepositoryRiskSchema,
    SecuritySummarySchema
)


class DashboardService:
    """
    Business layer for dashboard
    metrics and analytics.
    """

    def __init__(self, repository: DashboardRepository):
        self.repository = repository

    def calculate_security_score(self, risk_distribution: dict):
        total = sum(risk_distribution.values())
        if total == 0:
            return 100
        critical = risk_distribution.get("critical", 0)
        high = risk_distribution.get("high", 0)
        penalty = (critical * 10) + (high * 5)
        return max(100 - penalty, 0)

    def build_risk_distribution(self, data: dict):
        return RiskDistributionSchema(
            critical=data.get("critical", 0),
            high=data.get("high", 0),
            medium=data.get("medium", 0),
            low=data.get("low", 0)
        )

    def get_risky_commits(self):
        commits = self.repository.get_top_risky_commits()
        return [
            RiskCommitSchema(
                commit_id=item.commit_id,
                risk_score=item.risk_score,
                risk_level=item.risk_level,
                blocked=item.deployment_blocked
            )
            for item in commits
        ]

    def get_risk_trends(self):
        trends = self.repository.get_recent_risk_trend()
        return [
            RiskTrendPointSchema(
                date=item["date"],
                score=item["score"],
                level=(
                    "High" if item["score"] >= 70
                    else "Medium" if item["score"] >= 40
                    else "Low"
                )
            )
            for item in trends
        ]

    def get_repository_metrics(self):
        repositories = self.repository.get_repository_risk()
        return [
            RepositoryRiskSchema(
                repository=item["repository"],
                average_risk=item["average_risk"]
            )
            for item in repositories
        ]

    def get_dashboard(self):
        summary = self.repository.get_dashboard_summary()

        risk_distribution = self.build_risk_distribution(
            summary["risk_distribution"]
        )

        security_score = self.calculate_security_score(
            summary["risk_distribution"]
        )

        security_summary = SecuritySummarySchema(
            total_security_findings=summary.get("critical_findings", 0),
            critical_security_findings=summary.get("critical_findings", 0)
        )

        return {
            "overview": {
                "total_commits": summary["total_commits"],
                "total_analysis": summary["total_analysis"],
                "risk_distribution": risk_distribution,
                "blocked_deployments": summary["blocked_deployments"]
            },
            "risky_commits": self.get_risky_commits(),
            "security_summary": security_summary,
            "risk_trends": self.get_risk_trends(),
            "repositories": self.get_repository_metrics(),
            "security_score": security_score,
            "generated_at": datetime.utcnow()
        }
