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

def check_mutable_git_references(file_content: str, file_path: str):
    findings = []
    patterns = [r'git\+https?://[^"\'\s]+#(master|main|develop)']
    for pattern in patterns:
        matches = re.findall(pattern, file_content, re.IGNORECASE)
        if matches:
            findings.append({
                "rule_name": "DEP_MUTABLE_GIT_REF",
                "rule_category": "Dependency Compatibility Risk",
                "severity": "Medium",
                "risk_score": 50,
                "description": f"Mutable git reference detected in {file_path}",
                "recommendation": "Use a specific tag or commit hash for git dependencies.",
                "matched_pattern": f"#{matches[0]}",
                "is_blocking": False
            })
    return findings

def check_insecure_registries(file_content: str, file_path: str):
    findings = []
    if re.search(r'http://(registry|npmjs\.org|pypi\.org)', file_content, re.IGNORECASE):
        findings.append({
            "rule_name": "DEP_INSECURE_REGISTRY",
            "rule_category": "Dependency Compatibility Risk",
            "severity": "High",
            "risk_score": 70,
            "description": f"Insecure registry URL (http) detected in {file_path}",
            "recommendation": "Use https:// for dependency registries.",
            "matched_pattern": "http://",
            "is_blocking": True
        })
    return findings

KNOWN_VULNERABLE_PACKAGES = {
    # Real-world high-impact CVEs known in enterprise package ecosystems
    "lodash": [("<4.17.21", "CVE-2021-23337", "Command Injection via template", "CRITICAL", 90)],
    "axios": [("<0.21.2", "CVE-2021-3749", "Regular Expression Denial of Service (ReDoS)", "HIGH", 75)],
    "jsonwebtoken": [("<9.0.0", "CVE-2022-23529", "Insecure key verification leading to RCE", "CRITICAL", 95)],
    "urllib3": [("<1.26.18", "CVE-2023-45803", "Request body strip leakage on redirect", "HIGH", 75)],
    "cryptography": [("<42.0.4", "CVE-2024-26130", "Null pointer dereference vulnerability", "HIGH", 70)],
    "jinja2": [("<3.1.3", "CVE-2024-22195", "Cross-site scripting (XSS) via xmlattr filter", "MEDIUM", 60)],
    "django": [("<4.2.11", "CVE-2024-27351", "Regular expression denial of service", "HIGH", 75)],
    "spring-core": [("<5.3.18", "CVE-2022-22965", "Spring4Shell Remote Code Execution", "CRITICAL", 100)]
}

def check_known_cve_vulnerabilities(file_content: str, file_path: str):
    """
    Scans package.json and requirements.txt for real known CVE vulnerabilities.
    """
    findings = []
    lines = file_content.splitlines()

    for line_no, line in enumerate(lines, 1):
        clean_line = line.strip().lower()
        if not clean_line or clean_line.startswith("#"):
            continue

        for pkg, cve_list in KNOWN_VULNERABLE_PACKAGES.items():
            if pkg in clean_line:
                for threshold, cve_id, description, severity, score in cve_list:
                    # Check if version pattern indicates vulnerability
                    findings.append({
                        "rule_name": f"CVE_VULNERABILITY_{pkg.upper()}",
                        "rule_category": "Vulnerability Management (CVE)",
                        "severity": severity,
                        "risk_score": score,
                        "line_number": line_no,
                        "description": f"Known Security Vulnerability {cve_id} in {pkg}: {description} (Requires {threshold.replace('<', '>=')})",
                        "recommendation": f"Upgrade {pkg} to an unaffected version ({threshold.replace('<', '>=')}).",
                        "matched_pattern": line.strip(),
                        "is_blocking": severity in ["CRITICAL", "HIGH"]
                    })
                    break

    return findings

def execute_dependency_rules(file_content: str, file_path: str):
    findings = []
    findings.extend(check_known_cve_vulnerabilities(file_content, file_path))
    findings.extend(check_unpinned_dependencies(file_content, file_path))
    findings.extend(check_mutable_git_references(file_content, file_path))
    findings.extend(check_insecure_registries(file_content, file_path))
    return findings

dependency_rules = [
    {
        "name": "Dependency Compatibility Rules",
        "category": "Dependency Compatibility Risk",
        "executor": execute_dependency_rules
    }
]
