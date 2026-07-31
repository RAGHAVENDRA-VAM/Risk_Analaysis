from datetime import datetime

from app.services.rule_engine_service import RuleEngineService
from app.services.genai_risk_analyzer_service import GenAIRiskAnalyzer
from app.services.risk_aggregator import RiskAggregator
from app.services.recommendation_generator import RecommendationGenerator
from app.agents import CoordinatorAgent


class RiskAnalysisService:
    """
    Main workflow orchestrator.

    Connects:

    Rule Engine
        +
    Azure OpenAI
        +
    Risk Aggregator
        +
    Recommendation Engine

    """

    def __init__(self):
        self.rule_engine = RuleEngineService()
        self.ai_analyzer = GenAIRiskAnalyzer()
        self.risk_aggregator = RiskAggregator()
        self.recommendation_generator = RecommendationGenerator()
        self.coordinator = CoordinatorAgent()

    def analyze_commit(
        self,
        commit_id: str,
        branch: str,
        changed_files: list
    ):
        """
        Complete commit risk analysis.
        """

        # Step 1 - Run deterministic rules
        rule_result = self.rule_engine.execute(changed_files)

        # Step 2 - Generate AI analysis
        ai_result = self.ai_analyzer.analyze(
            {"commit_id": commit_id, "branch": branch},
            rule_result.get("findings", [])
        )

        # Step 3 - Combine rule + AI score
        final_result = self.risk_aggregator.aggregate(
            rule_result.get("findings", []),
            ai_result
        )

        # Step 4 - Generate remediation
        recommendations = self.recommendation_generator.generate(
            rule_result.get("findings", []),
            ai_result
        )
        agent_summary = self.coordinator.coordinate(rule_result.get("findings", []))

        return {
            "commit_id": commit_id,
            "branch": branch,
            "risk_score": final_result["risk_score"],
            "severity": final_result["severity"],
            "decision": final_result["decision"],
            "findings": rule_result.get("findings", []),
            "ai_analysis": ai_result,
            "recommendations": recommendations,
            "agent_summary": agent_summary,
            "created_at": datetime.utcnow()
        }

    def analyze_pull_request(
        self,
        pull_request_id: str,
        repository: str,
        branch: str,
        changed_files: list
    ):
        result = self.analyze_commit(
            pull_request_id,
            branch,
            changed_files
        )
        result["repository"] = repository
        result["pull_request_id"] = pull_request_id
        return result

    def should_block_deployment(self, analysis_result: dict):
        return analysis_result.get("decision") == "BLOCK_DEPLOYMENT"


risk_analysis_service = RiskAnalysisService()
