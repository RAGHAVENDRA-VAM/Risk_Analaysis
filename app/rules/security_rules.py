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





class SecurityRules:
    """
    Application security rules.
    """



    def __init__(self):

        self.name = "security"





    def evaluate(
        self,
        context: Dict
    ) -> List[Dict]:

        """
        Execute security checks.
        """



        findings = []



        for file in context.get(

            "files",

            []

        ):


            content = file.get(

                "content",

                ""

            )


            path = file.get(

                "path",

                ""

            )



            findings.extend(

                self.check_hardcoded_password(

                    path,

                    content

                )

            )


            findings.extend(

                self.check_api_keys(

                    path,

                    content

                )

            )


            findings.extend(

                self.check_private_keys(

                    path,

                    content

                )

            )


            findings.extend(

                self.check_debug_mode(

                    path,

                    content

                )

            )



        return findings





    def check_hardcoded_password(
        self,
        path: str,
        content: str
    ):

        """
        Detect passwords stored in code.
        """



        findings = []



        patterns = [

            "password=",

            "passwd=",

            "db_password"

        ]



        for pattern in patterns:


            if pattern.lower() in content.lower():


                findings.append(

                    {


                    "rule":

                        "SEC_HARDCODED_PASSWORD",


                    "title":

                        "Hardcoded Password Detected",


                    "severity":

                        "CRITICAL",


                    "score":

                        100,


                    "file":

                        path,


                    "description":

                        "Password value found inside source code"


                    }

                )


                break



        return findings





    def check_api_keys(
        self,
        path: str,
        content: str
    ):

        """
        Detect API keys and tokens.
        """



        findings = []



        keywords = [

            "api_key",

            "apikey",

            "secret_key",

            "access_token",

            "client_secret"

        ]



        for keyword in keywords:


            if keyword.lower() in content.lower():


                findings.append(

                    {


                    "rule":

                        "SEC_SECRET_EXPOSURE",


                    "title":

                        "Sensitive Secret Detected",


                    "severity":

                        "CRITICAL",


                    "score":

                        100,


                    "file":

                        path,


                    "description":

                        "Possible API key or secret found"


                    }

                )


                break



        return findings





    def check_private_keys(
        self,
        path: str,
        content: str
    ):

        """
        Detect private keys.
        """



        findings = []



        if "BEGIN PRIVATE KEY" in content:


            findings.append(

                {


                "rule":

                    "SEC_PRIVATE_KEY",


                "title":

                    "Private Key Exposure",


                "severity":

                    "CRITICAL",


                "score":

                    100,


                "file":

                    path,


                "description":

                    "Private key detected in repository"


                }

            )



        return findings





    def check_debug_mode(
        self,
        path: str,
        content: str
    ):

        """
        Detect enabled debug settings.
        """



        findings = []



        if (

            "DEBUG=True"

            in content

            or

            "debug=true"

            in content.lower()

        ):


            findings.append(

                {


                "rule":

                    "SEC_DEBUG_ENABLED",


                "title":

                    "Debug Mode Enabled",


                "severity":

                    "MEDIUM",


                "score":

                    40,


                "file":

                    path,


                "description":

                    "Application debug mode enabled"


                }

            )



        return findings