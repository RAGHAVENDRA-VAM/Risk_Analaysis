from sqlalchemy.orm import Session

from app.models.analysis_history import AnalysisHistory


class AnalysisHistoryRepository:
    """Repository for client-facing analysis history; keeps it separate from risk facts."""
    def __init__(self, db: Session):
        self.db = db

    def save(self, analysis_type: str, subject_id: str, result: dict, repository_name: str | None = None, branch_name: str | None = None) -> AnalysisHistory:
        record = AnalysisHistory(
            analysis_type=analysis_type, subject_id=subject_id, repository_name=repository_name,
            branch_name=branch_name, risk_score=result.get("risk_score", 0), severity=result.get("severity", "Low"),
            decision=result.get("decision", "ALLOW"), confidence=result.get("ai_analysis", {}).get("confidence", 0.0),
            findings=result.get("findings", []), summary=result.get("ai_analysis", {}).get("explanation"),
        )
        self.db.add(record); self.db.commit(); self.db.refresh(record)
        return record

    def list(self, repository_name: str | None = None, limit: int = 50) -> list[AnalysisHistory]:
        query = self.db.query(AnalysisHistory)
        if repository_name:
            query = query.filter(AnalysisHistory.repository_name == repository_name)
        return query.order_by(AnalysisHistory.created_at.desc()).limit(min(limit, 200)).all()
