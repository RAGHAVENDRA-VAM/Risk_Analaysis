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


Provide:

1. Risk summary
2. Business impact
3. Technical explanation
4. Remediation steps
5. Risk confidence score


Return JSON only.

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


                    temperature=0.2

                )

            )



            result = response.choices[0].message.content



            return json.loads(

                result

            )



        except Exception as error:


            logger.error(

                f"AI analysis failed {error}"

            )



            return {


                "risk_level":
                "UNKNOWN",


                "explanation":
                "AI analysis unavailable",


                "confidence":
                0

            }