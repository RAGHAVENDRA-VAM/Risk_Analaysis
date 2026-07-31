from typing import (
    List,
    Dict
)


from app.core.logging import (
    get_logger
)





logger = get_logger(
    __name__
)





class RecommendationGenerator:
    """
    Generates remediation actions
    for detected risks.
    """



    def __init__(self):

        self.recommendation_map = {


            "TF_PUBLIC_STORAGE":

            [

                "Disable public network access",

                "Configure Azure Private Endpoint",

                "Restrict storage firewall rules",

                "Enable storage monitoring"

            ],



            "TF_OPEN_NSG_RULE":

            [

                "Remove 0.0.0.0/0 inbound access",

                "Restrict source IP ranges",

                "Use private networking"

            ],



            "SEC_SECRET_EXPOSURE":

            [

                "Remove secret from source code",

                "Rotate exposed credentials",

                "Store secrets in Azure Key Vault"

            ],



            "SEC_HARDCODED_PASSWORD":

            [

                "Remove password from code",

                "Use managed identity",

                "Use secret management service"

            ],



            "K8S_PRIVILEGED_CONTAINER":

            [

                "Disable privileged mode",

                "Configure Kubernetes securityContext",

                "Run container as non-root"

            ],



            "K8S_LATEST_IMAGE":

            [

                "Use versioned container image tags",

                "Avoid latest tag in production"

            ],



            "PIPELINE_SECRET_EXPOSURE":

            [

                "Move secrets to secure variables",

                "Use Azure Key Vault integration",

                "Enable secret scanning"

            ]

        }





    def generate_for_finding(
        self,
        finding: Dict,
        ai_result: Dict = None
    ):

        """
        Generate recommendation
        for single finding.
        """



        rule = finding.get(

            "rule",

            ""

        )



        recommendations = (

            self.recommendation_map.get(

                rule,

                [

                "Review security configuration",

                "Follow DevSecOps best practices"

                ]

            )

        )



        return {


            "rule":

                rule,


            "issue":

                finding.get(

                    "title"

                ),


            "severity":

                finding.get(

                    "severity"

                ),


            "description":

                finding.get(

                    "description"

                ),


            "ai_explanation":

                ai_result.get(

                    "explanation"

                )

                if ai_result

                else None,


            "recommendations":

                recommendations,

            "estimated_fix_time": "15-30 minutes" if finding.get("severity") in {"Critical", "High", "CRITICAL", "HIGH"} else "5-15 minutes",
            "compliance": ["CIS", "OWASP", "SOC 2"],
            "reference_links": [],
            "suggested_code_fix": finding.get("suggested_code_fix")

        }





    def generate(
        self,
        findings: List[Dict],
        ai_result: Dict
    ):

        """
        Generate all recommendations.
        """



        recommendations = []



        for finding in findings:


            recommendations.append(

                self.generate_for_finding(

                    finding,

                    ai_result

                )

            )



        logger.info(

            f"Generated {len(recommendations)} recommendations"

        )



        return recommendations
