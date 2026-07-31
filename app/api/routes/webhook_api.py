from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Any, Dict

from app.services.commit_processor_service import CommitProcessorService
from app.services.risk_analysis_service import risk_analysis_service
from app.services.azure_devops_service import AzureDevOpsService
from app.services.analysis_response_service import analysis_response_service
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
            return await handle_push(resource, db)

        elif event_type in ("git.pullrequest.created", "git.pullrequest.updated"):
            return await handle_pull_request(resource, db)

        elif event_type in ("build.completed", "release.deployment.completed"):
            return {"status": "received", "event_type": event_type}

        else:
            return {"status": "ok", "event_type": event_type}

    except Exception as error:
        logger.error(f"Webhook error: {error}")
        return {"status": "error", "detail": str(error)}


async def handle_push(resource: dict, db):
    commits = resource.get("commits", [])

    if not commits:
        return {"status": "ok", "reason": "no commits in payload"}

    commit = commits[0]
    repository_data = resource.get("repository", {})
    project = repository_data.get("project", {}).get("name", "")
    repository_id = repository_data.get("id", "")
    commit_id = commit.get("commitId", "unknown")
    commit_data = {
        "commit_id": commit_id,
        "message": commit.get("comment", ""),
        "author": commit.get("author", {}).get("name", "unknown"),
        "repository_name": repository_data.get("name", ""),
        "branch_name": (resource.get("refUpdates") or [{}])[0].get("name", ""),
        "files": []
    }

    try:
        client = AzureDevOpsService()
        await client.get_commit(project, repository_id, commit_id)
        commit_data["files"] = await client.get_commit_changed_files(project, repository_id, commit_id)
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


async def handle_pull_request(resource: dict, db):
    pr_id = resource.get("pullRequestId")
    repository_data = resource.get("repository", {})
    repository_name = repository_data.get("name", "")
    repository_id = repository_data.get("id", "")
    project = resource.get("project", {}).get("name", "")
    source_branch = resource.get("sourceRefName", "")
    title = resource.get("title", "")

    logger.info(f"PR #{pr_id} '{title}' in {repository_name}")

    try:
        client = AzureDevOpsService()
        pr = await client.get_pull_request(project, repository_id, pr_id)
        source_version = pr.get("lastMergeSourceCommit", {}).get("commitId", "")
        files = await client.get_changed_files(project, repository_id, pr_id, source_version)
        result = risk_analysis_service.analyze_pull_request(
            pull_request_id=str(pr_id),
            repository=repository_name,
            branch=source_branch,
            changed_files=files
        )
        result["repository"] = repository_name

        repository = RiskRepository(db)
        repository.save_complete_analysis(result)

        client_result = analysis_response_service.to_client_response(result)
        await client.create_pr_comment(
            project,
            repository_id,
            pr_id,
            f"AI DevOps Risk Analyzer: **{client_result['severity']}** risk "
            f"({client_result['riskScore']}/100). Decision: **{client_result['decision']}**."
        )
        for finding in client_result["findings"]:
            if finding["severity"] in {"Critical", "High"} and finding["filePath"]:
                await client.create_pr_thread(project, repository_id, pr_id, finding["description"], finding["filePath"], finding["lineNumber"])
        await client.create_status(
            project, repository_id, pr_id,
            "failed" if client_result["severity"] == "Critical" else "succeeded",
            f"{client_result['severity']} risk: {client_result['riskScore']}/100"
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
