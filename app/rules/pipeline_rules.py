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



class PipelineRules:
    """
    CI/CD pipeline security rules.
    """

    def __init__(self):

        self.name = "pipeline"



    def evaluate(
        self,
        context: Dict
    ) -> List[Dict]:

        """
        Execute pipeline checks.
        """

        findings = []


        for file in context.get(
            "files",
            []
        ):

            if file.get(
                "category"
            ) != "pipeline":

                continue


            path = file.get(
                "path",
                ""
            )


            content = file.get(
                "content",
                ""
            )


            findings.extend(
                self.check_secrets(
                    path,
                    content
                )
            )


            findings.extend(
                self.check_security_scans(
                    path,
                    content
                )
            )


            findings.extend(
                self.check_production_approval(
                    path,
                    content
                )
            )


            findings.extend(
                self.check_unsafe_scripts(
                    path,
                    content
                )
            )


        return findings



    def check_secrets(
        self,
        path: str,
        content: str
    ):

        """
        Detect secrets in pipeline files.
        """

        findings = []


        keywords = [

            "password",

            "client_secret",

            "access_token",

            "api_key",

            "connection_string"

        ]


        for keyword in keywords:

            if keyword.lower() in content.lower():

                findings.append(

                    {

                    "rule":
                        "PIPELINE_SECRET_EXPOSURE",


                    "title":
                        "Secret Found In Pipeline",


                    "severity":
                        "CRITICAL",


                    "score":
                        100,


                    "file":
                        path,


                    "description":
                        "Sensitive value detected in pipeline YAML"

                    }

                )

                break


        return findings



    def check_security_scans(
        self,
        path: str,
        content: str
    ):

        """
        Detect missing security tools.
        """

        findings = []


        security_tools = [

            "sonarqube",

            "sonarcloud",

            "trivy",

            "semgrep",

            "gitleaks"

        ]


        has_scan = any(

            tool in content.lower()

            for tool in security_tools

        )


        if not has_scan:


            findings.append(

                {

                "rule":
                    "PIPELINE_MISSING_SECURITY_SCAN",


                "title":
                    "Security Scan Missing",


                "severity":
                    "HIGH",


                "score":
                    75,


                "file":
                    path,


                "description":
                    "CI/CD pipeline does not contain security scanning"

                }

            )


        return findings



    def check_production_approval(
        self,
        path: str,
        content: str
    ):

        """
        Detect production deployment without approval.
        """

        findings = []


        production_keywords = [

            "production",

            "prod",

            "release"

        ]


        if any(

            item in content.lower()

            for item in production_keywords

        ):


            if "approval" not in content.lower():


                findings.append(

                    {

                    "rule":
                        "PIPELINE_NO_APPROVAL_GATE",


                    "title":
                        "Production Approval Missing",


                    "severity":
                        "HIGH",


                    "score":
                        80,


                    "file":
                        path,


                    "description":
                        "Production deployment lacks approval control"

                    }

                )


        return findings



    def check_unsafe_scripts(
        self,
        path: str,
        content: str
    ):

        """
        Detect dangerous pipeline commands.
        """

        findings = []


        dangerous_commands = [

            "curl | bash",

            "chmod 777",

            "rm -rf /"

        ]


        for command in dangerous_commands:


            if command in content:


                findings.append(

                    {

                    "rule":
                        "PIPELINE_UNSAFE_COMMAND",


                    "title":
                        "Unsafe Pipeline Command",


                    "severity":
                        "MEDIUM",


                    "score":
                        50,


                    "file":
                        path,


                    "description":
                        f"Dangerous command detected: {command}"

                    }

                )


        return findings


def _execute_pipeline_rules(file_content: str, file_path: str):
    instance = PipelineRules()
    return instance.evaluate({"files": [{"path": file_path, "content": file_content, "category": "pipeline"}]})


pipeline_rules = [
    {
        "name": "Pipeline Security Rules",
        "category": "CI/CD",
        "executor": _execute_pipeline_rules
    }
]
