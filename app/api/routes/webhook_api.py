from fastapi import APIRouter, Request, Depends
from app.services.commit_processor_service import CommitProcessorService
from app.services.risk_analysis_service import risk_analysis_service
from app.core.logging import get_logger
from app.core.database import get_db

logger = get_logger(__name__)

router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.post("/azure-devops")
async def azure_devops_webhook(request: Request, db=Depends(get_db)):
    try:
        payload = await request.json()
        event_type = payload.get("eventType", "")

        logger.info(f"Azure DevOps event received: {event_type}")

        if event_type == "git.push":
            return handle_push(payload, db)

        elif event_type in ("git.pullrequest.created", "git.pullrequest.updated"):
            return handle_pull_request(payload)

        else:
            # Unknown or test event — return 200 so Azure DevOps marks hook as healthy
            return {"status": "ok", "event_type": event_type}

    except Exception as error:
        logger.error(f"Webhook error: {error}")
        # Still return 200 so Azure DevOps does not mark the hook as failed
        return {"status": "error", "detail": str(error)}


def handle_push(payload: dict, db):
    resource = payload.get("resource", {})
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
        return {"status": "analysis_started", "commit_id": result.get("commit_id")}
    except Exception as e:
        logger.error(f"Push processing failed: {e}")
        return {"status": "error", "detail": str(e)}


def handle_pull_request(payload: dict):
    resource = payload.get("resource", {})
    pr_id = resource.get("pullRequestId")
    repository = resource.get("repository", {}).get("name", "")
    source_branch = resource.get("sourceRefName", "")
    title = resource.get("title", "")

    logger.info(f"PR #{pr_id} '{title}' in {repository}")

    try:
        result = risk_analysis_service.analyze_pull_request(
            pull_request_id=str(pr_id),
            repository=repository,
            branch=source_branch,
            changed_files=[]
        )
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
