from datetime import datetime, timedelta


from sqlalchemy.orm import Session


from sqlalchemy import func


from app.models.commit import (
    Commit
)


from app.models.risk_analysis import (
    RiskAnalysis
)


from app.models.risk_finding import (
    RiskFinding
)





class DashboardRepository:
    """
    Repository for dashboard
    aggregation queries.
    """



    def __init__(
        self,
        db: Session
    ):

        self.db = db





    def get_total_commits(
        self
    ):


        return (

            self.db.query(
                func.count(
                    Commit.id
                )
            )

            .scalar()

        )





    def get_total_analysis(
        self
    ):


        return (

            self.db.query(
                func.count(
                    RiskAnalysis.id
                )
            )

            .scalar()

        )





    def get_risk_distribution(
        self
    ):


        result = (

            self.db.query(

                RiskAnalysis.risk_level,

                func.count(
                    RiskAnalysis.id
                )

            )

            .group_by(

                RiskAnalysis.risk_level

            )

            .all()

        )



        distribution = {


            "critical":
                0,


            "high":
                0,


            "medium":
                0,


            "low":
                0

        }



        for level, count in result:


            if level:


                distribution[
                    level.lower()
                ] = count



        return distribution





    def get_blocked_deployments(
        self
    ):


        return (

            self.db.query(
                func.count(
                    RiskAnalysis.id
                )
            )

            .filter(

                RiskAnalysis.deployment_blocked
                ==
                True

            )

            .scalar()

        )





    def get_critical_findings_count(
        self
    ):


        return (

            self.db.query(

                func.count(
                    RiskFinding.id
                )

            )

            .filter(

                RiskFinding.severity
                ==
                "Critical"

            )

            .scalar()

        )





    def get_recent_risk_trend(
        self,
        days: int = 30
    ):


        start_date = (

            datetime.utcnow()

            -
            timedelta(
                days=days
            )

        )



        result = (

            self.db.query(

                func.date(
                    RiskAnalysis.created_at
                ),

                func.avg(
                    RiskAnalysis.risk_score
                )

            )

            .filter(

                RiskAnalysis.created_at
                >=
                start_date

            )

            .group_by(

                func.date(
                    RiskAnalysis.created_at
                )

            )

            .order_by(

                func.date(
                    RiskAnalysis.created_at
                )

            )

            .all()

        )



        return [

            {

                "date":
                    str(date),


                "score":
                    round(
                        float(score)
                    )

            }


            for date, score in result

        ]





    def get_repository_risk(
        self
    ):


        result = (

            self.db.query(

                Commit.repository_name,

                func.avg(
                    RiskAnalysis.risk_score
                )

            )

            .join(

                RiskAnalysis,

                Commit.commit_id
                ==
                RiskAnalysis.commit_id

            )

            .group_by(

                Commit.repository_name

            )

            .all()

        )



        return [

            {

                "repository":
                    repo,


                "average_risk":
                    round(
                        float(score),
                        2
                    )

            }


            for repo, score in result

        ]





    def get_top_risky_commits(
        self,
        limit: int = 10
    ):


        return (

            self.db.query(
                RiskAnalysis
            )

            .order_by(

                RiskAnalysis.risk_score.desc()

            )

            .limit(
                limit
            )

            .all()

        )





    def get_dashboard_summary(
        self
    ):


        return {


            "total_commits":

                self.get_total_commits(),



            "total_analysis":

                self.get_total_analysis(),



            "risk_distribution":

                self.get_risk_distribution(),



            "blocked_deployments":

                self.get_blocked_deployments(),



            "critical_findings":

                self.get_critical_findings_count()

        }





