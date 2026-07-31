"""Specialist agents that enrich the existing deterministic/GenAI workflow.

They are deliberately small and deterministic: model inference remains in the
existing GenAIRiskAnalyzer service, not in clients or individual agents.
"""
from __future__ import annotations
from collections import Counter
from typing import Any


class SpecialistAgent:
    name = "general"
    categories: set[str] = set()
    def analyze(self, findings: list[dict[str, Any]]) -> dict[str, Any]:
        matched = [item for item in findings if not self.categories or (item.get("category") or item.get("rule_category")) in self.categories]
        return {"agent": self.name, "findings": len(matched), "risk": max((item.get("score", item.get("risk_score", 0)) for item in matched), default=0)}


class SecurityAgent(SpecialistAgent): name, categories = "security", {"Security"}
class TerraformAgent(SpecialistAgent): name, categories = "terraform", {"Infrastructure"}
class KubernetesAgent(SpecialistAgent): name, categories = "kubernetes", {"Kubernetes"}
class PipelineAgent(SpecialistAgent): name, categories = "pipeline", {"CI/CD"}
class CloudAgent(SpecialistAgent): name, categories = "cloud", {"Infrastructure", "Kubernetes"}
class ComplianceAgent(SpecialistAgent): name, categories = "compliance", {"Security", "Infrastructure", "Kubernetes", "CI/CD"}
class RecommendationAgent(SpecialistAgent): name = "recommendation"
class RiskAggregationAgent(SpecialistAgent): name = "risk-aggregation"


class CoordinatorAgent:
    def __init__(self) -> None:
        self.agents = [SecurityAgent(), TerraformAgent(), KubernetesAgent(), PipelineAgent(), CloudAgent(), ComplianceAgent(), RecommendationAgent(), RiskAggregationAgent()]

    def coordinate(self, findings: list[dict[str, Any]]) -> dict[str, Any]:
        categories = Counter((item.get("category") or item.get("rule_category") or "General") for item in findings)
        return {"specialists": [agent.analyze(findings) for agent in self.agents], "category_counts": dict(categories)}
