from fastapi import (
    APIRouter,
    Depends
)


from sqlalchemy.orm import Session


from app.core.database import (
    get_db
)


from app.services.dashboard_service import (
    DashboardService
)


from app.repositories.dashboard_repository import (
    DashboardRepository
)





router = APIRouter(

    prefix="/dashboard",

    tags=["Dashboard"]

)





def get_dashboard_service(
    db: Session = Depends(get_db)
):


    repository = DashboardRepository(
        db
    )


    return DashboardService(
        repository
    )





@router.get("/summary")
async def dashboard_summary(
    service: DashboardService =
        Depends(get_dashboard_service)
):

    """
    Returns complete dashboard overview.

    Response:

    {
        total_commits,
        risk_distribution,
        blocked_deployments,
        security_score
    }

    """



    return (

        service.get_dashboard()

    )





@router.get("/risk-distribution")
async def risk_distribution(
    service: DashboardService =
        Depends(get_dashboard_service)
):


    dashboard = (

        service.get_dashboard()

    )


    return {


        "risk_distribution":

            dashboard[
                "overview"
            ][
                "risk_distribution"
            ]

    }





@router.get("/security-score")
async def security_score(
    service: DashboardService =
        Depends(get_dashboard_service)
):


    dashboard = (

        service.get_dashboard()

    )


    return {


        "security_score":

            dashboard[
                "security_score"
            ]

    }





@router.get("/risk-trends")
async def risk_trends(
    service: DashboardService =
        Depends(get_dashboard_service)
):


    dashboard = (

        service.get_dashboard()

    )


    return {


        "trend":

            dashboard[
                "risk_trends"
            ]

    }





@router.get("/repositories")
async def repository_risk(
    service: DashboardService =
        Depends(get_dashboard_service)
):


    dashboard = (

        service.get_dashboard()

    )


    return {


        "repositories":

            dashboard[
                "repositories"
            ]

    }





@router.get("/risky-commits")
async def risky_commits(
    service: DashboardService =
        Depends(get_dashboard_service)
):


    dashboard = (

        service.get_dashboard()

    )


    return {


        "commits":

            dashboard[
                "risky_commits"
            ]

    }





@router.get("/executive-summary")
async def executive_summary(
    service: DashboardService =
        Depends(get_dashboard_service)
):


    dashboard = (

        service.get_dashboard()

    )



    overview = (

        dashboard[
            "overview"
        ]

    )



    return {


        "summary":

            {

                "total_changes":

                    overview[
                        "total_analysis"
                    ],


                "blocked_releases":

                    overview[
                        "blocked_deployments"
                    ],


                "security_score":

                    dashboard[
                        "security_score"
                    ],


                "overall_status":

                    (

                        "Healthy"

                        if dashboard[
                            "security_score"
                        ] >= 80

                        else

                        "Needs Attention"

                    )

            }

    }





@router.get("/health")
async def dashboard_health():


    return {


        "service":

            "dashboard-api",


        "status":

            "healthy"

    }