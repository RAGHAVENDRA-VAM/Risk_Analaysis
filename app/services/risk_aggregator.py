from typing import List, Dict


from app.core.logging import get_logger


logger = get_logger(__name__)


class RiskAggregator:
    """
    Combines all risk signals
    and generates deployment decision.
    """

    def __init__(self):
        self.block_threshold = 85

        self.warning_threshold = 60

    def calculate_rule_score(self, findings: List[Dict]):
        """
        Calculate score from rules.
        """

        if not findings:
            return 0

        scores = []

        for finding in findings:
            scores.append(finding.get("score", 0))

        #
        # Cumulative score capped at 100
        #

        total_score = sum(scores)
        return min(100, total_score)

    def calculate_ai_score(self, ai_result: Dict):
        """
        Convert AI confidence/risk
        into numeric score.
        """

        try:
            confidence = float(ai_result.get("confidence", 0) or 0)
        except (ValueError, TypeError):
            confidence = 0.0

        risk_level = str(ai_result.get("risk_level", "") or "")

        multiplier = {"LOW": 30, "MEDIUM": 60, "HIGH": 80, "CRITICAL": 100}

        base_score = multiplier.get(risk_level.upper(), 0)

        return int(base_score * confidence)

    def calculate_final_score(self, rule_score: int, ai_score: int):
        """
        Combine rule and AI score.
        """

        final_score = (rule_score * 0.7) + (ai_score * 0.3)

        return round(final_score)

    def get_severity(self, score: int):
        """
        Convert score to severity.
        """

        if score >= 86:
            return "CRITICAL"

        if score >= 61:
            return "HIGH"

        if score >= 31:
            return "MEDIUM"

        return "LOW"

    def get_decision(self, score: int):
        """
        Deployment decision.
        """

        if score >= self.block_threshold:
            return "BLOCK_DEPLOYMENT"

        if score >= self.warning_threshold:
            return "REQUIRE_APPROVAL"

        return "ALLOW_DEPLOYMENT"

    def aggregate(self, findings: List[Dict], ai_result: Dict):
        """
        Generate final risk decision.
        """

        rule_score = self.calculate_rule_score(findings)

        ai_score = self.calculate_ai_score(ai_result)

        final_score = self.calculate_final_score(rule_score, ai_score)

        result = {
            "rule_score": rule_score,
            "ai_score": ai_score,
            "risk_score": final_score,
            "severity": self.get_severity(final_score),
            "decision": self.get_decision(final_score),
        }

        logger.info(f"Final risk decision {result}")

        return result
