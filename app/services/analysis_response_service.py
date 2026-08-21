"""Adapters for presenting existing risk-analysis results to API clients."""

from __future__ import annotations

from typing import Any


class AnalysisResponseService:
    """Keeps client response shaping separate from analysis and persistence."""

    @staticmethod
    def _line_number(finding: dict[str, Any]) -> int:
        return int(finding.get("line_number") or finding.get("line") or 1)

    def to_client_response(self, result: dict[str, Any]) -> dict[str, Any]:
        recommendation_by_rule = {item.get("rule"): item for item in result.get("recommendations", [])}
        findings = []
        for index, finding in enumerate(result.get("findings", []), start=1):
            recommendation = recommendation_by_rule.get(finding.get("rule") or finding.get("rule_name"), {})
            findings.append({
                "id": finding.get("id", index),
                "severity": finding.get("severity", "Low"),
                "ruleName": finding.get("rule") or finding.get("rule_name", "AI_REVIEW"),
                "category": finding.get("rule_category") or finding.get("category", "Security"),
                "filePath": finding.get("file_path") or finding.get("file") or finding.get("path", ""),
                "lineNumber": self._line_number(finding),
                "title": finding.get("title") or finding.get("rule", "Risk finding"),
                "description": finding.get("description", ""),
                "businessImpact": finding.get("business_impact", "Potential production security or reliability impact."),
                "compliance": recommendation.get("compliance", ["CIS", "OWASP"]),
                "estimatedFixTime": recommendation.get("estimated_fix_time", "15 minutes"),
                "recommendation": finding.get("recommendation") or "\n".join(recommendation.get("recommendations", ["Review the recommended remediation."])),
                "suggestedCodeFix": finding.get("suggested_code_fix") or recommendation.get("suggested_code_fix"),
                "referenceLinks": finding.get("reference_links") or recommendation.get("reference_links", []),
            })

        summary = {severity: 0 for severity in ("critical", "high", "medium", "low")}
        for finding in findings:
            key = finding["severity"].lower()
            if key in summary:
                summary[key] += 1

        return {
            "riskScore": result.get("risk_score", 0),
            "severity": result.get("severity", "Low"),
            "decision": result.get("decision", "ALLOW"),
            "confidence": result.get("ai_analysis", {}).get("confidence", 0.0),
            "engine": "rule+ai",
            "summary": summary,
            "findings": findings,
            "recommendations": result.get("recommendations", []),
            "scores": self._category_scores(findings),
            "agentSummary": result.get("agent_summary", {}),
        }

    @staticmethod
    def _category_scores(findings: list[dict[str, Any]]) -> dict[str, int]:
        """Client dashboard score by broad platform area."""
        scores = {"security": 0, "terraform": 0, "pipeline": 0, "kubernetes": 0, "docker": 0}
        for finding in findings:
            category = finding["category"].lower()
            file_path = finding["filePath"].lower()
            
            # Smart category inference since AI often defaults to "Security"
            if "docker" in file_path or "docker" in category:
                key = "docker"
            elif "kubernetes" in category or "deployment.yaml" in file_path or "k8s" in file_path:
                key = "kubernetes"
            elif "pipeline" in category or "ci/cd" in category or "azure-pipelines" in file_path or ".github/workflows" in file_path:
                key = "pipeline"
            elif "infrastructure" in category or "terraform" in category or file_path.endswith(".tf"):
                key = "terraform"
            else:
                key = "security"
                
            severity = finding.get("severity", "Low").title()
            scores[key] = max(scores[key], 100 if severity in {"Critical", "High"} else 60 if severity == "Medium" else 25)
        return scores


analysis_response_service = AnalysisResponseService()
