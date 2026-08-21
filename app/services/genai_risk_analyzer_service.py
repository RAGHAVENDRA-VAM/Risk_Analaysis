import json
from urllib.parse import urlparse

from typing import (
    Dict,
    List
)

from app.core.config import (
    settings
)

from app.core.logging import (
    get_logger
)

# pyrefly: ignore [missing-import]
from openai import AzureOpenAI





logger = get_logger(
    __name__
)





class GenAIRiskAnalyzer:
    """
    AI based DevOps risk analyzer.
    """



    def __init__(self):

        self.client = AzureOpenAI(

            azure_endpoint=

                self._normalize_endpoint(

                    settings.AZURE_OPENAI_ENDPOINT

                ),


            api_key=

                settings.AZURE_OPENAI_API_KEY,


            api_version=

                settings.AZURE_OPENAI_API_VERSION

        )


        self.deployment = (

            settings.AZURE_OPENAI_DEPLOYMENT_NAME

        )


    @staticmethod
    def _normalize_endpoint(endpoint: str) -> str:
        """
        Normalize Azure OpenAI resource endpoint.

        The Azure SDK expects the bare resource host (for example
        https://my-resource.openai.azure.com). If the configured URL
        includes /openai or /openai/v1, strip that suffix.
        """
        if not endpoint:
            return endpoint

        parsed = urlparse(endpoint)
        path = parsed.path.rstrip("/")

        if path.endswith("/openai/v1"):
            path = path[: -len("/openai/v1")]
        elif path.endswith("/openai"):
            path = path[: -len("/openai")]

        return parsed._replace(path=path).geturl()





    def build_prompt(
        self,
        context: Dict,
        findings: List[Dict]
    ):

        """
        Create AI analysis prompt.
        """



        prompt = f"""

You are a senior DevSecOps engineer.

Analyze the following deployment change.

Commit Context:

{json.dumps(
    context,
    indent=2
)}


Security Findings:

{json.dumps(
    findings,
    indent=2
)}


Return ONLY a JSON object with the exact following keys:
{{
  "risk_level": "CRITICAL, HIGH, MEDIUM, or LOW",
  "confidence": <float between 0.0 and 1.0>,
  "summary": "<Risk summary>",
  "business_impact": "<Business impact>",
  "explanation": "<Technical explanation>",
  "remediation": "<Remediation steps>"
}}
"""



        return prompt





    def analyze(
        self,
        context: Dict,
        findings: List[Dict]
    ):

        """
        Execute AI risk analysis.
        """



        prompt = self.build_prompt(

            context,

            findings

        )



        try:


            response = (

                self.client.chat.completions.create(

                    model=self.deployment,


                    messages=[

                    {

                    "role":
                    "system",

                    "content":
                    "You are a DevSecOps AI assistant."

                    },


                    {

                    "role":
                    "user",

                    "content":
                    prompt

                    }

                    ],
                    response_format={"type": "json_object"}

                )

            )



            result = response.choices[0].message.content
            
            # Clean up potential markdown formatting (```json ... ```)
            if result.strip().startswith("```"):
                lines = result.strip().split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                result = "\n".join(lines)
                
            return json.loads(result)



        except Exception as error:
            logger.error(f"AI analysis failed: {error}")
            return {
                "risk_level": "UNKNOWN",
                "explanation": f"AI analysis failed: {str(error)}",
                "confidence": 0,
                "summary": f"Error: {str(error)}",
                "business_impact": "Unknown due to AI failure",
                "remediation": "Check Azure OpenAI configuration"
            }
