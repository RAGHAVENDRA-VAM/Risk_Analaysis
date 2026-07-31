"""Adapters for presenting existing risk-analysis results to API clients."""

from __future__ import annotations

from typing import Any


class AnalysisResponseService:
    """Keeps client response shaping separate from analysis and persistence."""

    @staticmethod
    def _line_number(finding: dict[str, Any]) -> int:
        return int(finding.get("line_number") or finding.get("line") or 1)

    def to_client_response(self, result: dict[str, Any]) -> dict[str, Any]:
        findings = []
        for index, finding in enumerate(result.get("findings", []), start=1):
            findings.append({
                "id": finding.get("id", index),
                "severity": finding.get("severity", "Low"),
                "ruleName": finding.get("rule") or finding.get("rule_name", "AI_REVIEW"),
                "category": finding.get("rule_category") or finding.get("category", "Security"),
                "filePath": finding.get("file_path") or finding.get("path", ""),
                "lineNumber": self._line_number(finding),
                "title": finding.get("title") or finding.get("rule", "Risk finding"),
                "description": finding.get("description", ""),
                "businessImpact": finding.get("business_impact", "Review before deployment."),
                "recommendation": finding.get("recommendation", "Review the recommended remediation."),
                "suggestedCodeFix": finding.get("suggested_code_fix"),
                "referenceLinks": finding.get("reference_links", []),
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
        }


analysis_response_service = AnalysisResponseService()
