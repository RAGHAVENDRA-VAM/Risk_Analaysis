from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)

from pydantic import BaseModel

from app.repositories.risk_repository import (
    RiskRepository
)


from app.repositories.finding_repository import (
    FindingRepository
)


from app.repositories.recommendation_repository import (
    RecommendationRepository
)


from app.core.database import (
    get_db
)


from app.core.logging import (
    get_logger
)

from app.services.risk_analysis_service import risk_analysis_service


logger = get_logger(
    __name__
)


router = APIRouter(

    prefix="/risk",

    tags=["Risk Analysis"]

)


class PRAnalyzeRequest(BaseModel):
    project: str
    repository: str
    repositoryId: str
    pullRequestId: int
    sourceBranch: str
    targetBranch: str
    organization: str
    user: str
    files: list = []


@router.post("/analyze")
async def analyze_pull_request(request: PRAnalyzeRequest, db=Depends(get_db)):
    """
    Triggered by the Azure DevOps extension when a PR is opened.
    Runs rule engine + AI analysis and returns risk result.
    """
    try:
        result = risk_analysis_service.analyze_pull_request(
            pull_request_id=str(request.pullRequestId),
            repository=request.repository,
            branch=request.sourceBranch,
            changed_files=request.files
        )

        repository = RiskRepository(db)
        analysis, saved_findings = repository.save_complete_analysis(result)

        finding_lookup = {
            finding.rule_name: finding.id
            for finding in saved_findings
            if finding.rule_name
        }

        RecommendationRepository(db).save_recommendations(
            result["commit_id"],
            result["recommendations"],
            finding_lookup
        )

        return {
            "riskScore": result["risk_score"],
            "severity": result["severity"],
            "decision": result["decision"],
            "confidence": result.get("ai_analysis", {}).get("confidence", 0.0),
            "analysisTime": 0,
            "engine": "rule+ai",
            "summary": {
                "critical": sum(1 for f in result["findings"] if f.get("severity") == "Critical"),
                "high": sum(1 for f in result["findings"] if f.get("severity") == "High"),
                "medium": sum(1 for f in result["findings"] if f.get("severity") == "Medium"),
                "low": sum(1 for f in result["findings"] if f.get("severity") == "Low")
            },
            "findings": result["findings"],
            "recommendations": result["recommendations"]
        }
    except Exception as e:
        logger.error(f"PR analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))





@router.get(
    "/{commit_id}"
)
async def get_risk_summary(
    commit_id: str,
    db=Depends(get_db)
):

    """
    Return complete risk summary.
    """



    repository = RiskRepository(

        db

    )



    risk = repository.get_analysis_by_commit(

        commit_id

    )



    if not risk:


        raise HTTPException(

            status_code=404,

            detail="Risk analysis not found"

        )



    return {


        "commit_id":

            commit_id,


        "risk_score":

            risk.risk_score,


        "severity":

            risk.severity,


        "decision":

            risk.decision,


        "created_at":

            risk.created_at

    }





@router.get(
    "/{commit_id}/findings"
)
async def get_findings(
    commit_id: str,
    db=Depends(get_db)
):

    """
    Return security findings.
    """



    risk_repo = RiskRepository(

        db

    )



    analysis = risk_repo.get_analysis_by_commit(

        commit_id

    )



    if not analysis:

        raise HTTPException(

            status_code=404,

            detail="Risk analysis not found"

        )



    repository = FindingRepository(

        db

    )



    findings = repository.get_findings_by_commit(

        analysis.commit_id

    )

    findings_response = [
        {
            "id": finding.id,
            "commit_id": finding.commit_id,
            "file_path": finding.file_path,
            "rule_name": finding.rule_name,
            "category": finding.category,
            "title": finding.title,
            "description": finding.description,
            "severity": finding.severity,
            "risk_score": finding.risk_score,
            "status": finding.status,
            "created_at": finding.created_at
        }
        for finding in findings
    ]

    return {

        "commit_id": commit_id,
        "findings": findings_response
    }




@router.get(
    "/{commit_id}/recommendations"
)
async def get_recommendations(
    commit_id: str,
    db=Depends(get_db)
):

    """
    Return remediation suggestions.
    """



    recommendations = (

        RecommendationRepository(

            db

        ).get_by_commit_id(

            commit_id

        )

    )



    recommendations_response = [
        {
            "id": recommendation.id,
            "finding_id": recommendation.finding_id,
            "commit_id": recommendation.commit_id,
            "title": recommendation.title,
            "description": recommendation.description,
            "remediation_steps": recommendation.remediation_steps,
            "priority": recommendation.priority,
            "status": recommendation.status,
            "created_at": recommendation.created_at,
            "updated_at": recommendation.updated_at
        }
        for recommendation in recommendations
    ]

    return {
        "commit_id": commit_id,
        "recommendations": recommendations_response
    }