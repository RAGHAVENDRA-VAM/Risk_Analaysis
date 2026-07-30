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
