import re

def check_unpinned_dependencies(file_content: str, file_path: str):
    findings = []
    
    if "package.json" in file_path.lower():
        # Match "package": "*" or "package": "latest" or "package": ">=1.0.0" without upper bound
        patterns = [
            r'"[^"]+"\s*:\s*"\*"',
            r'"[^"]+"\s*:\s*"latest"',
            r'"[^"]+"\s*:\s*">=\d+\.\d+\.\d+"(?!\s*<)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, file_content, re.IGNORECASE)
            if matches:
                findings.append({
                    "rule_name": "DEP_UNPINNED_VERSION",
                    "rule_category": "Dependency Compatibility Risk",
                    "severity": "High",
                    "risk_score": 75,
                    "description": f"Unpinned dependency version detected in {file_path}",
                    "recommendation": "Pin dependency to a specific version or use a lockfile.",
                    "matched_pattern": str(matches[0]),
                    "is_blocking": False
                })

    elif "requirements.txt" in file_path.lower():
        # Match package>=1.0.0 (without upper bound) or package without version
        lines = file_content.splitlines()
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                if "==" not in line and (">=" in line and "<" not in line or re.match(r'^[a-zA-Z0-9_\-]+$', line)):
                    findings.append({
                        "rule_name": "DEP_UNPINNED_VERSION",
                        "rule_category": "Dependency Compatibility Risk",
                        "severity": "Medium",
                        "risk_score": 50,
                        "description": f"Unpinned dependency detected in {file_path}",
                        "recommendation": "Pin dependency to a specific version using '=='.",
                        "matched_pattern": line,
                        "is_blocking": False
                    })
                    break # One finding per file is enough for this rule

    return findings

def execute_dependency_rules(file_content: str, file_path: str):
    findings = []
    findings.extend(check_unpinned_dependencies(file_content, file_path))
    return findings

dependency_rules = [
    {
        "name": "Dependency Compatibility Rules",
        "category": "Dependency Compatibility Risk",
        "executor": execute_dependency_rules
    }
]
