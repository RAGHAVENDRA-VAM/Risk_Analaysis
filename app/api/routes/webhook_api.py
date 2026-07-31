from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Any, Dict

from app.services.commit_processor_service import CommitProcessorService
from app.services.risk_analysis_service import risk_analysis_service
from app.repositories.risk_repository import RiskRepository
from app.core.logging import get_logger
from app.core.database import get_db

logger = get_logger(__name__)

router = APIRouter(prefix="/webhook", tags=["Webhook"])


class WebhookPayload(BaseModel):
    eventType: str = ""
    resource: Dict[str, Any] = {}


@router.post("/azure-devops")
async def azure_devops_webhook(payload: WebhookPayload, db=Depends(get_db)):
    try:
        event_type = payload.eventType
        resource = payload.resource

        logger.info(f"Azure DevOps event received: {event_type}")

        if event_type == "git.push":
            return handle_push(resource, db)

        elif event_type in ("git.pullrequest.created", "git.pullrequest.updated"):
            return handle_pull_request(resource, db)

        else:
            return {"status": "ok", "event_type": event_type}

    except Exception as error:
        logger.error(f"Webhook error: {error}")
        return {"status": "error", "detail": str(error)}


def handle_push(resource: dict, db):
    commits = resource.get("commits", [])

    if not commits:
        return {"status": "ok", "reason": "no commits in payload"}

    commit = commits[0]
    commit_data = {
        "commit_id": commit.get("commitId", "unknown"),
        "message": commit.get("comment", ""),
        "author": commit.get("author", {}).get("name", "unknown"),
        "repository_name": resource.get("repository", {}).get("name", ""),
        "branch_name": (resource.get("refUpdates") or [{}])[0].get("name", ""),
        "files": []
    }

    try:
        processor = CommitProcessorService(db)
        result = processor.process_commit(commit_data)

        analysis_result = risk_analysis_service.analyze_commit(
            commit_id=result.get("commit_id"),
            branch=commit_data["branch_name"],
            changed_files=commit_data["files"]
        )
        analysis_result["repository"] = commit_data["repository_name"]

        repository = RiskRepository(db)
        repository.save_complete_analysis(analysis_result)

        return {
            "status": "analysis_complete",
            "commit_id": result.get("commit_id"),
            "risk_score": analysis_result.get("risk_score"),
            "severity": analysis_result.get("severity"),
            "decision": analysis_result.get("decision")
        }
    except Exception as e:
        logger.error(f"Push processing failed: {e}")
        return {"status": "error", "detail": str(e)}


def handle_pull_request(resource: dict, db):
    pr_id = resource.get("pullRequestId")
    repository_name = resource.get("repository", {}).get("name", "")
    source_branch = resource.get("sourceRefName", "")
    title = resource.get("title", "")

    logger.info(f"PR #{pr_id} '{title}' in {repository_name}")

    try:
        result = risk_analysis_service.analyze_pull_request(
            pull_request_id=str(pr_id),
            repository=repository_name,
            branch=source_branch,
            changed_files=[]
        )
        result["repository"] = repository_name

        repository = RiskRepository(db)
        repository.save_complete_analysis(result)

        return {
            "status": "analysis_complete",
            "pull_request_id": pr_id,
            "risk_score": result["risk_score"],
            "severity": result["severity"],
            "decision": result["decision"]
        }
    except Exception as e:
        logger.error(f"PR analysis failed: {e}")
        return {"status": "error", "detail": str(e)}
