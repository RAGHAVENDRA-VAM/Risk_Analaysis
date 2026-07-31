import os

from app.rules import get_all_rules



class RuleEngineService:
    """
    Executes deterministic risk rules
    against changed files.
    """



    def __init__(self):

        self.rules = (
            get_all_rules()
        )



    def detect_file_type(
        self,
        file_path: str
    ):

        extension = (
            os.path.splitext(
                file_path
            )[1]
            .lower()
        )


        return extension





    def select_applicable_rules(
        self,
        file_path: str
    ):

        extension = (
            self.detect_file_type(
                file_path
            )
        )


        selected_rules = []



        for rule in self.rules:


            category = (
                rule["category"]
            )


            #
            # Infrastructure files
            #

            if category == "Infrastructure":


                if extension in [

                    ".tf",

                    ".tfvars"

                ]:

                    selected_rules.append(
                        rule
                    )



            #
            # Kubernetes manifests
            #

            elif category == "Kubernetes":


                if (

                    extension in [

                        ".yaml",

                        ".yml"

                    ]

                    and

                    (

                        "deployment"

                        in file_path.lower()

                        or

                        "service"

                        in file_path.lower()

                        or

                        "k8s"

                        in file_path.lower()

                    )

                ):

                    selected_rules.append(
                        rule
                    )



            #
            # CI/CD Pipeline files
            #

            elif category == "CI/CD":


                if (

                    "pipeline"

                    in file_path.lower()

                    or

                    "azure-pipelines"

                    in file_path.lower()

                    or

                    ".github"

                    in file_path.lower()

                ):

                    selected_rules.append(
                        rule
                    )



            #
            # Security checks
            #

            elif category == "Security":


                selected_rules.append(
                    rule
                )



            #
            # Application code
            #

            elif category == "Code Quality":


                if extension in [

                    ".py",

                    ".java",

                    ".cs",

                    ".js",

                    ".ts",

                    ".jsx",

                    ".tsx"

                ]:

                    selected_rules.append(
                        rule
                    )

            elif category == "Container":
                if os.path.basename(file_path).lower() == "dockerfile":
                    selected_rules.append(rule)

            elif category == "Cloud":
                if extension in [".bicep", ".json", ".sh", ".ps1"] or "ansible" in file_path.lower() or "jenkinsfile" in file_path.lower():
                    selected_rules.append(rule)



        return selected_rules





    def analyze_file(
        self,
        file_content: str,
        file_path: str
    ):

        findings = []


        applicable_rules = (

            self.select_applicable_rules(
                file_path
            )

        )



        for rule in applicable_rules:


            executor = (
                rule["executor"]
            )


            results = executor(

                file_content,

                file_path

            )


            findings.extend(
                results
            )



        return findings





    def analyze_files(
        self,
        files: list
    ):

        """
        Analyze multiple changed files.

        Expected input:

        [
            {
                "path": "main.tf",
                "content": "..."
            }
        ]

        """


        all_findings = []



        for file in files:


            findings = (

                self.analyze_file(

                    file["content"],

                    file["path"]

                )

            )


            all_findings.extend(
                findings
            )



        return all_findings





    def calculate_risk_score(
        self,
        findings: list
    ):


        if not findings:

            return 0



        total_score = sum(

            item.get("score", item.get("risk_score", 0))

            for item in findings

        )



        #
        # Normalize score
        #

        score = min(

            total_score,

            100

        )


        return score





    def determine_risk_level(
        self,
        score: int
    ):


        if score >= 90:

            return "Critical"


        elif score >= 70:

            return "High"


        elif score >= 40:

            return "Medium"


        else:

            return "Low"





    def execute(
        self,
        files: list
    ):

        findings = (

            self.analyze_files(
                files
            )

        )


        risk_score = (

            self.calculate_risk_score(
                findings
            )

        )


        risk_level = (

            self.determine_risk_level(
                risk_score
            )

        )


        blocking_findings = [

            item

            for item in findings

            if item.get(
                "is_blocking",
                False
            )

        ]



        return {

            "findings":
                findings,


            "risk_score":
                risk_score,


            "risk_level":
                risk_level,


            "deployment_blocked":
                len(blocking_findings) > 0,


            "blocking_findings":
                blocking_findings

        }





rule_engine_service = (
    RuleEngineService()
)
