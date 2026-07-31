from typing import Dict, List, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation


class RecommendationRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_commit_id(self, commit_id: str) -> list:
        return (
            self.db.query(Recommendation)
            .filter(Recommendation.commit_id == commit_id)
            .order_by(desc(Recommendation.created_at))
            .all()
        )

    def get_by_priority(self, priority: str) -> list:
        return (
            self.db.query(Recommendation)
            .filter(Recommendation.priority == priority)
            .order_by(desc(Recommendation.created_at))
            .all()
        )

    def get_by_status(self, status: str) -> list:
        return (
            self.db.query(Recommendation)
            .filter(Recommendation.status == status)
            .order_by(desc(Recommendation.created_at))
            .all()
        )

    def save_recommendations(
        self,
        commit_id: str,
        recommendations: list,
        finding_lookup: Optional[Dict[str, int]] = None
    ) -> list:
        finding_lookup = finding_lookup or {}
        saved_recommendations = []

        for recommendation in recommendations:
            remediation_steps = recommendation.get("recommendations")
            if isinstance(remediation_steps, list):
                remediation_steps = "\n".join(remediation_steps)

            saved_recommendation = Recommendation(
                finding_id=
                    finding_lookup.get(
                        recommendation.get("rule"),
                        0
                    ),
                commit_id=commit_id,
                title=(
                    recommendation.get("issue")
                    or recommendation.get("rule")
                ),
                description=recommendation.get("description", ""),
                remediation_steps=remediation_steps,
                priority=recommendation.get("severity", "Medium")
            )

            self.db.add(saved_recommendation)
            saved_recommendations.append(saved_recommendation)

        self.db.commit()
        return saved_recommendations

    def get_pending(self) -> list:
        return (
            self.db.query(Recommendation)
            .filter(Recommendation.status == "Pending")
            .order_by(desc(Recommendation.created_at))
            .all()
        )

    def get_statistics(self):
        return (
            self.db.query(
                Recommendation.priority,
                func.count(Recommendation.id).label("total")
            )
            .group_by(Recommendation.priority)
            .all()
        )
