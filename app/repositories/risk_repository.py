from datetime import datetime


from sqlalchemy.orm import Session


from app.models.risk_analysis import (
    RiskAnalysis
)


from app.models.risk_finding import (
    RiskFinding
)





class RiskRepository:
    """
    Database repository for
    DevOps risk analysis data.
    """



    def __init__(
        self,
        db: Session
    ):

        self.db = db





    def save_analysis(
        self,
        analysis_data: dict
    ):


        analysis = RiskAnalysis(

            commit_id=
                analysis_data.get(
                    "commit_id"
                ),


            repository=
                analysis_data.get(
                    "repository"
                ),


            branch=
                analysis_data.get(
                    "branch"
                ),


            risk_score=
                analysis_data.get(
                    "risk_score"
                ),


            risk_level=
                analysis_data.get(
                    "risk_level"
                ),


            deployment_decision=
                analysis_data.get(
                    "deployment_decision"
                ),


            deployment_blocked=
                analysis_data.get(
                    "deployment_blocked"
                ),


            approval_required=
                analysis_data.get(
                    "approval_required"
                ),


            created_at=
                datetime.utcnow()

        )



        self.db.add(
            analysis
        )


        self.db.commit()


        self.db.refresh(
            analysis
        )


        return analysis





    def save_findings(
        self,
        commit_id: str,
        findings: list
    ):

        saved_findings = []

        for finding in findings:
            risk_finding = RiskFinding(
                commit_id=commit_id,
                file_path=finding.get("file_path"),
                rule_name=(
                    finding.get("rule")
                    or finding.get("rule_name")
                ),
                category=(
                    finding.get("rule_category")
                    or finding.get("category")
                ),
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




    def save_complete_analysis(
        self,
        analysis_result: dict
    ):


        analysis = (

            self.save_analysis(

                analysis_result

            )

        )


        findings = (

            analysis_result.get(

                "findings",

                []

            )

        )


        saved_findings = self.save_findings(

            analysis.commit_id,

            findings

        )


        return analysis, saved_findings




    def get_analysis_by_commit(
        self,
        commit_id: str
    ):


        return (

            self.db.query(
                RiskAnalysis
            )

            .filter(

                RiskAnalysis.commit_id
                ==
                commit_id

            )

            .first()

        )





    def get_recent_analysis(
        self,
        limit: int = 20
    ):


        return (

            self.db.query(
                RiskAnalysis
            )

            .order_by(

                RiskAnalysis.created_at.desc()

            )

            .limit(
                limit
            )

            .all()

        )





    def get_blocked_deployments(
        self
    ):


        return (

            self.db.query(
                RiskAnalysis
            )

            .filter(

                RiskAnalysis.deployment_blocked
                ==
                True

            )

            .order_by(

                RiskAnalysis.created_at.desc()

            )

            .all()

        )





    def get_high_risk_changes(
        self
    ):


        return (

            self.db.query(
                RiskAnalysis
            )

            .filter(

                RiskAnalysis.risk_score >= 70

            )

            .order_by(

                RiskAnalysis.risk_score.desc()

            )

            .all()

        )





risk_repository = RiskRepository