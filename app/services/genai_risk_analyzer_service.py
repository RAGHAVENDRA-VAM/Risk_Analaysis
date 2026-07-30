import json


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

                settings.AZURE_OPENAI_ENDPOINT,


            api_key=

                settings.AZURE_OPENAI_API_KEY,


            api_version=

                settings.AZURE_OPENAI_API_VERSION

        )


        self.deployment = (

            settings.AZURE_OPENAI_DEPLOYMENT_NAME

        )





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