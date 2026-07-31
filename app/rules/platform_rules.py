"""Additional deterministic checks for cloud/automation formats not covered by legacy rules."""
from __future__ import annotations
from typing import Any


def _finding(rule: str, title: str, severity: str, score: int, path: str, description: str, line: int = 1) -> dict[str, Any]:
    return {"rule": rule, "title": title, "severity": severity, "score": score, "file_path": path, "line_number": line, "description": description, "category": "Cloud" if rule.startswith("CLOUD") else "Container" if rule.startswith("DOCKER") else "Automation"}


def _line(content: str, needle: str) -> int:
    return next((number for number, value in enumerate(content.splitlines(), 1) if needle.lower() in value.lower()), 1)


def container_rules(content: str, path: str) -> list[dict[str, Any]]:
    if path.rsplit("/", 1)[-1].lower() != "dockerfile": return []
    findings = []
    if ":latest" in content:
        findings.append(_finding("DOCKER_LATEST_TAG", "Mutable Docker image tag", "Medium", 45, path, "Pin the image to an immutable version or digest.", _line(content, ":latest")))
    if "USER " not in content.upper():
        findings.append(_finding("DOCKER_ROOT_USER", "Container runs as root", "High", 75, path, "Set a non-root USER in the Dockerfile."))
    return findings


def cloud_rules(content: str, path: str) -> list[dict[str, Any]]:
    suffix = path.lower().rsplit(".", 1)[-1]
    findings = []
    if suffix in {"bicep", "json"} and any(term in content.lower() for term in ("publicipaddress", "publicnetworkaccess", "0.0.0.0/0")):
        findings.append(_finding("CLOUD_PUBLIC_EXPOSURE", "Public cloud exposure", "High", 75, path, "Restrict public access and use private networking.", _line(content, "public")))
    if suffix in {"sh", "ps1"} and "curl " in content.lower() and "| sh" in content.lower():
        findings.append(_finding("AUTOMATION_UNVERIFIED_DOWNLOAD", "Unverified script download", "High", 70, path, "Download, verify, and execute scripts as separate steps.", _line(content, "curl")))
    return findings


platform_rules = [
    {"name": "Container Rules", "category": "Container", "executor": container_rules},
    {"name": "Cloud and Automation Rules", "category": "Cloud", "executor": cloud_rules},
]
