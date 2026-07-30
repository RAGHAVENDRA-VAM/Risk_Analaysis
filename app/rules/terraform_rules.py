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





class TerraformRules:
    """
    Terraform security rules.
    """



    def __init__(self):

        self.name = "terraform"





    def evaluate(
        self,
        context: Dict
    ) -> List[Dict]:

        """
        Execute Terraform checks.
        """



        findings = []



        files = context.get(

            "files",

            []

        )



        for file in files:


            if file.get(

                "category"

            ) != "terraform":


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

                self.check_public_storage(

                    path,

                    content

                )

            )


            findings.extend(

                self.check_open_network_rules(

                    path,

                    content

                )

            )


            findings.extend(

                self.check_public_ip(

                    path,

                    content

                )

            )


            findings.extend(

                self.check_missing_encryption(

                    path,

                    content

                )

            )



        return findings





    def check_public_storage(
        self,
        path: str,
        content: str
    ):

        """
        Detect public Azure storage exposure.
        """



        findings = []



        if (

            "azurerm_storage_account"

            in content

            and

            "public_network_access_enabled = true"

            in content

        ):


            findings.append(

                {


                "rule":

                    "TF_PUBLIC_STORAGE",


                "title":

                    "Public Storage Account Exposure",


                "severity":

                    "HIGH",


                "score":

                    90,


                "file":

                    path,


                "description":

                    "Azure storage account allows public network access"


                }

            )



        return findings





    def check_open_network_rules(
        self,
        path: str,
        content: str
    ):

        """
        Detect open NSG rules.
        """



        findings = []



        if (

            "azurerm_network_security_rule"

            in content

            and

            "0.0.0.0/0"

            in content

        ):


            findings.append(

                {


                "rule":

                    "TF_OPEN_NSG_RULE",


                "title":

                    "Open Network Security Rule",


                "severity":

                    "CRITICAL",


                "score":

                    100,


                "file":

                    path,


                "description":

                    "Network rule allows traffic from internet"


                }

            )



        return findings





    def check_public_ip(
        self,
        path: str,
        content: str
    ):

        """
        Detect public IP exposure.
        """



        findings = []



        if (

            "azurerm_public_ip"

            in content

        ):


            findings.append(

                {


                "rule":

                    "TF_PUBLIC_IP",


                "title":

                    "Public IP Resource Created",


                "severity":

                    "MEDIUM",


                "score":

                    50,


                "file":

                    path,


                "description":

                    "Infrastructure creates public internet exposure"


                }

            )



        return findings





    def check_missing_encryption(
        self,
        path: str,
        content: str
    ):

        """
        Detect missing encryption configuration.
        """



        findings = []



        if (

            "azurerm_storage_account"

            in content

            and

            "encryption"

            not in content

        ):


            findings.append(

                {


                "rule":

                    "TF_MISSING_ENCRYPTION",


                "title":

                    "Missing Storage Encryption",


                "severity":

                    "HIGH",


                "score":

                    80,


                "file":

                    path,


                "description":

                    "Storage encryption configuration not found"


                }

            )



        return findings


def _execute_terraform_rules(file_content: str, file_path: str):
    instance = TerraformRules()
    return instance.evaluate({"files": [{"path": file_path, "content": file_content, "category": "terraform"}]})


terraform_rules = [
    {
        "name": "Terraform Security Rules",
        "category": "Infrastructure",
        "executor": _execute_terraform_rules
    }
]
