from datetime import datetime


from sqlalchemy.orm import Session


from sqlalchemy import func


from app.models.risk_finding import (
    RiskFinding
)





class FindingRepository:
    """
    Repository layer for
    risk finding management.
    """



    def __init__(
        self,
        db: Session
    ):

        self.db = db





    def save_finding(
        self,
        commit_id: str,
        finding: dict
    ):

        risk_finding = RiskFinding(
            commit_id=commit_id,
            rule_name=finding.get("rule_name"),
            category=finding.get("rule_category"),
            severity=finding.get("severity"),
            risk_score=finding.get("risk_score"),
            description=finding.get("description"),
            status="OPEN",
            created_at=datetime.utcnow()
        )


        self.db.add(
            risk_finding
        )


        self.db.commit()


        self.db.refresh(
            risk_finding
        )


        return risk_finding





    def save_findings(
        self,
        commit_id: str,
        findings: list
    ):

        saved = []

        for finding in findings:
            result = self.save_finding(
                commit_id,
                finding
            )
            saved.append(result)

        return saved





    def get_findings_by_commit(
        self,
        commit_id: str
    ):

        return (
            self.db.query(
                RiskFinding
            )
            .filter(
                RiskFinding.commit_id == commit_id
            )
            .order_by(
                RiskFinding.risk_score.desc()
            )
            .all()
        )





    def get_critical_findings(
        self
    ):


        return (

            self.db.query(
                RiskFinding
            )

            .filter(

                RiskFinding.severity
                ==
                "Critical"

            )

            .order_by(

                RiskFinding.created_at.desc()

            )

            .all()

        )





    def get_blocking_findings(
        self
    ):

        return (
            self.db.query(
                RiskFinding
            )
            .order_by(
                RiskFinding.created_at.desc()
            )
            .all()
        )





    def get_findings_by_category(
        self,
        category: str
    ):


        return (

            self.db.query(
                RiskFinding
            )

            .filter(

                RiskFinding.category
                ==
                category

            )

            .order_by(

                RiskFinding.risk_score.desc()

            )

            .all()

        )





    def count_by_severity(
        self
    ):


        result = (

            self.db.query(

                RiskFinding.severity,

                func.count(
                    RiskFinding.id
                )

            )

            .group_by(

                RiskFinding.severity

            )

            .all()

        )



        return {

            severity:
                count

            for severity, count in result

        }





    def count_by_category(
        self
    ):


        result = (

            self.db.query(

                RiskFinding.category,

                func.count(
                    RiskFinding.id
                )

            )

            .group_by(

                RiskFinding.category

            )

            .all()

        )


        return {

            category:
                count

            for category, count in result

        }





    def delete_commit_findings(
        self,
        commit_id: str
    ):

        (
            self.db.query(
                RiskFinding
            )
            .filter(
                RiskFinding.commit_id == commit_id
            )
            .delete()
        )

        self.db.commit()





finding_repository = FindingRepository