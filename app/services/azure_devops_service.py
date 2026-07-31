"""Azure DevOps REST client used by service hooks; no analysis occurs here."""

from __future__ import annotations

from base64 import b64encode
import asyncio
from typing import Any

import httpx

from app.core.config import settings


class AzureDevOpsService:
    def __init__(self, organization: str | None = None) -> None:
        self.organization = organization or settings.AZURE_DEVOPS_ORGANIZATION
        if not self.organization or not settings.AZURE_DEVOPS_PAT:
            raise ValueError("AZURE_DEVOPS_ORGANIZATION and AZURE_DEVOPS_PAT must be configured")
        token = b64encode(f":{settings.AZURE_DEVOPS_PAT}".encode()).decode()
        self.headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}
        self.base_url = f"https://dev.azure.com/{self.organization}"

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.request(method, f"{self.base_url}{path}", headers=self.headers, **kwargs)
                    response.raise_for_status()
                    return response.json() if response.content else None
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError):
                if attempt == 2:
                    raise
                await asyncio.sleep(0.5 * (2 ** attempt))
        raise RuntimeError("Unreachable retry state")

    async def get_pull_request(self, project: str, repository_id: str, pull_request_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/{project}/_apis/git/repositories/{repository_id}/pullrequests/{pull_request_id}?api-version=7.1")

    async def get_changed_files(self, project: str, repository_id: str, pull_request_id: int, version: str) -> list[dict[str, str]]:
        iterations = await self._request("GET", f"/{project}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/iterations?api-version=7.1")
        if not iterations.get("value"):
            return []
        iteration_id = iterations["value"][-1]["id"]
        changes = await self._request("GET", f"/{project}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/iterations/{iteration_id}/changes?api-version=7.1")
        files = []
        for change in changes.get("changeEntries", []):
            path = change.get("item", {}).get("path")
            if not path or change.get("changeType") == "delete":
                continue
            content = await self.get_file_content(project, repository_id, path, version)
            files.append({"path": path, "content": content, "change_type": "modified"})
        return files

    async def get_commit(self, project: str, repository_id: str, commit_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/{project}/_apis/git/repositories/{repository_id}/commits/{commit_id}?api-version=7.1")

    async def get_commit_changed_files(self, project: str, repository_id: str, commit_id: str) -> list[dict[str, str]]:
        """Get content for the paths changed by a commit, excluding deletions."""
        changes = await self._request("GET", f"/{project}/_apis/git/repositories/{repository_id}/commits/{commit_id}/changes?api-version=7.1")
        files = []
        for change in changes.get("changes", []):
            path = change.get("item", {}).get("path")
            if not path or change.get("changeType") == "delete":
                continue
            files.append({"path": path, "content": await self.get_file_content(project, repository_id, path, commit_id), "change_type": "modified"})
        return files

    async def get_file_content(self, project: str, repository_id: str, path: str, version: str) -> str:
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.get(f"{self.base_url}/{project}/_apis/git/repositories/{repository_id}/items", headers=self.headers, params={"path": path, "versionDescriptor.version": version, "includeContent": "true", "api-version": "7.1"})
                    response.raise_for_status()
                    return response.text
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError):
                if attempt == 2:
                    raise
                await asyncio.sleep(0.5 * (2 ** attempt))
        raise RuntimeError("Unreachable retry state")

    async def get_repository_information(self, project: str, repository_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/{project}/_apis/git/repositories/{repository_id}?api-version=7.1")

    async def create_pr_thread(self, project: str, repository_id: str, pull_request_id: int, content: str, file_path: str | None = None, line: int | None = None) -> dict[str, Any]:
        thread: dict[str, Any] = {"comments": [{"parentCommentId": 0, "content": content, "commentType": 1}], "status": 1}
        if file_path and line:
            thread["threadContext"] = {"filePath": file_path, "rightFileStart": {"line": line, "offset": 1}, "rightFileEnd": {"line": line, "offset": 1}}
        return await self._request("POST", f"/{project}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/threads?api-version=7.1", json=thread)

    async def create_pr_comment(self, project: str, repository_id: str, pull_request_id: int, content: str) -> dict[str, Any]:
        return await self.create_pr_thread(project, repository_id, pull_request_id, content)

    async def create_status(self, project: str, repository_id: str, pull_request_id: int, state: str, description: str) -> dict[str, Any]:
        payload = {"state": state, "description": description, "context": {"name": "AI DevOps Risk Analyzer", "genre": "continuous-integration"}}
        return await self._request("POST", f"/{project}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/statuses?api-version=7.1", json=payload)
