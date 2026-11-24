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
        Calculate realistic score from rules based on actual highest severity and weighted findings.
        Avoids inflating score to 100 when only small or single issues exist.
        """
        if not findings:
            return 0

        # Base maximum severity anchor
        severity_weights = {
            "CRITICAL": 85,
            "HIGH": 65,
            "MEDIUM": 40,
            "LOW": 15
        }

        severities = [f.get("severity", "LOW").upper() for f in findings]
        
        # Max severity sets the baseline bracket
        if "CRITICAL" in severities:
            base = 85
            # Add minor delta for additional critical issues up to 100
            extra = (severities.count("CRITICAL") - 1) * 5 + severities.count("HIGH") * 2
            return min(100, base + extra)
        elif "HIGH" in severities:
            base = 65
            extra = (severities.count("HIGH") - 1) * 5 + severities.count("MEDIUM") * 2
            return min(80, base + extra)
        elif "MEDIUM" in severities:
            base = 40
            extra = (severities.count("MEDIUM") - 1) * 3
            return min(60, base + extra)
        else:
            base = 15
            extra = len(findings) * 2
            return min(30, base + extra)

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

    def calculate_final_score(self, rule_score: int, ai_score: int, ai_result: Dict = None):
        """
        Combine rule and AI score.
        """
        # If AI analysis is unavailable, failed, or has 0 confidence, rely 100% on the rule engine
        risk_level = ai_result.get("risk_level", "").upper() if ai_result else ""
        confidence = float(ai_result.get("confidence", 0) if ai_result else 0)
        
        if not ai_result or risk_level == "UNKNOWN" or confidence == 0:
            return rule_score

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
        final_score = self.calculate_final_score(rule_score, ai_score, ai_result)

        result = {
            "rule_score": rule_score,
            "ai_score": ai_score,
            "risk_score": final_score,
            "severity": self.get_severity(final_score),
            "decision": self.get_decision(final_score),
        }

        logger.info(f"Final risk decision {result}")

        return result
