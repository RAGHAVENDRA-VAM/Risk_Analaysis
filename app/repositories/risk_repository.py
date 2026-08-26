import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.risk_analysis import RiskAnalysis
from app.models.risk_finding import RiskFinding
from app.models.ai_token_usage import AITokenUsage

class RiskRepository:
    """
    Database repository for DevOps risk analysis data.
    """

    def __init__(self, db: Session):
        self.db = db

    def save_analysis(self, analysis_data: dict):
        analysis = RiskAnalysis(
            commit_id=analysis_data.get("commit_id"),
            repository_name=analysis_data.get("repository"),
            rule_score=analysis_data.get("rule_score"),
            ai_score=analysis_data.get("ai_score"),
            risk_score=analysis_data.get("risk_score"),
            severity=analysis_data.get("severity"),
            decision=analysis_data.get("decision"),
            ai_summary=json.dumps(analysis_data.get("ai_analysis", {})),
            confidence=analysis_data.get("ai_analysis", {}).get("confidence", 0.0),
            created_at=datetime.utcnow()
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def save_findings(self, commit_id: str, findings: list):
        saved_findings = []
        for finding in findings:
            risk_finding = RiskFinding(
                commit_id=commit_id,
                file_path=finding.get("file_path") or finding.get("file") or finding.get("path"),
                rule_name=(finding.get("rule") or finding.get("rule_name")),
                category=(finding.get("rule_category") or finding.get("category")),
                title=finding.get("title"),
                description=finding.get("description"),
                severity=finding.get("severity"),
                risk_score=finding.get("risk_score"),
                status="OPEN",
                created_at=datetime.utcnow()
            )
            self.db.add(risk_finding)
            saved_findings.append(risk_finding)
        self.db.commit()
        return saved_findings

    def save_complete_analysis(self, analysis_result: dict):
        analysis = self.save_analysis(analysis_result)
        findings = analysis_result.get("findings", [])
        saved_findings = self.save_findings(analysis.commit_id, findings)
        
        # Save token usage
        ai_analysis = analysis_result.get("ai_analysis", {})
        token_usage_data = ai_analysis.get("token_usage")
        if token_usage_data:
            token_usage = AITokenUsage(
                commit_id=analysis.commit_id,
                model_name=token_usage_data.get("model_name"),
                input_tokens=token_usage_data.get("input_tokens", 0),
                output_tokens=token_usage_data.get("output_tokens", 0),
                total_tokens=token_usage_data.get("total_tokens", 0),
                latency_ms=token_usage_data.get("latency_ms", 0)
            )
            self.db.add(token_usage)
            self.db.commit()
            
        return analysis, saved_findings

    def get_analysis_by_commit(self, commit_id: str):
        return self.db.query(RiskAnalysis).filter(RiskAnalysis.commit_id == commit_id).first()

    def get_recent_analysis(self, limit: int = 20):
        return self.db.query(RiskAnalysis).order_by(RiskAnalysis.created_at.desc()).limit(limit).all()

    def get_blocked_deployments(self):
        return self.db.query(RiskAnalysis).filter(RiskAnalysis.deployment_blocked == True).order_by(RiskAnalysis.created_at.desc()).all()

    def get_high_risk_changes(self):
        return self.db.query(RiskAnalysis).filter(RiskAnalysis.risk_score >= 70).order_by(RiskAnalysis.risk_score.desc()).all()

risk_repository = RiskRepository
