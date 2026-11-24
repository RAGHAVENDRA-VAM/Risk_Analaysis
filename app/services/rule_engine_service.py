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

                # Fallback: Apply generic text heuristics to all non-binary files
                binary_extensions = [
                    ".jpg", ".jpeg", ".png", ".gif", ".pdf", 
                    ".zip", ".tar", ".gz", ".exe", ".dll", ".so", ".bin",
                    ".class", ".pyc"
                ]
                
                if extension and extension not in binary_extensions:
                    selected_rules.append(
                        rule
                    )

            elif category == "Container":
                if os.path.basename(file_path).lower() == "dockerfile":
                    selected_rules.append(rule)

            elif category == "Cloud":
                if extension in [".bicep", ".json", ".sh", ".ps1"] or "ansible" in file_path.lower() or "jenkinsfile" in file_path.lower():
                    selected_rules.append(rule)

            elif category == "DB Impact Risk":
                if extension == ".sql":
                    selected_rules.append(rule)

            elif category == "Dependency Compatibility Risk":
                basename = os.path.basename(file_path).lower()
                if basename in ["package.json", "requirements.txt", "pom.xml"]:
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



        lines = file_content.splitlines()

        for rule in applicable_rules:


            executor = (
                rule["executor"]
            )


            results = executor(

                file_content,

                file_path

            )

            # Enrich findings with accurate line numbers and file path
            for item in results:
                if not item.get("file_path") and not item.get("file") and not item.get("path"):
                    item["file_path"] = file_path
                
                # If rule didn't compute an exact line number, calculate it dynamically from matched pattern or keywords
                if not item.get("line_number") or item.get("line_number") == 1:
                    needle = item.get("matched_pattern") or item.get("pattern") or ""
                    if needle:
                        found_line = next((idx for idx, val in enumerate(lines, 1) if str(needle).strip() in val), None)
                        if found_line:
                            item["line_number"] = found_line
                    
                    if not item.get("line_number") or item.get("line_number") == 1:
                        # Fallback: scan for any keyword in description or title
                        terms = [t for t in (item.get("title", "") + " " + item.get("description", "")).split() if len(t) > 3 and t.isalnum()]
                        for term in terms:
                            found = next((idx for idx, val in enumerate(lines, 1) if term.lower() in val.lower()), None)
                            if found:
                                item["line_number"] = found
                                break

            findings.extend(
                results
            )



        return findings





    def load_repo_policy(self, files: list) -> dict:
        """
        Loads .riskrc, .risk-policy.json, or .devops-risk.json if present in repo files.
        Allows enterprise teams to override thresholds and ignore specific rules.
        """
        import json
        for file in files:
            path = file.get("path", "").lower()
            if any(cfg in path for cfg in [".riskrc", ".risk-policy.json", ".devops-risk.json"]):
                try:
                    return json.loads(file.get("content", "{}"))
                except Exception:
                    pass
        return {}

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
        policy = self.load_repo_policy(files)
        ignored_rules = set(policy.get("ignore_rules", []))
        severity_overrides = policy.get("severity_overrides", {})



        for file in files:


            findings = (

                self.analyze_file(

                    file["content"],

                    file["path"]

                )

            )

            # Apply Enterprise Policy Overrides and Ignores
            filtered_findings = []
            for finding in findings:
                rule_name = finding.get("rule") or finding.get("rule_name")
                if rule_name in ignored_rules:
                    continue
                if rule_name in severity_overrides:
                    finding["severity"] = severity_overrides[rule_name]

                filtered_findings.append(finding)


            all_findings.extend(
                filtered_findings
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
