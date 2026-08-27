import re

def check_destructive_db_operations(file_content: str, file_path: str):
    findings = []
    
    destructive_patterns = [
        r"\bDROP\s+TABLE\b",
        r"\bTRUNCATE\s+TABLE\b",
        r"\bDROP\s+DATABASE\b",
        r"\bALTER\s+TABLE\s+.*\s+DROP\s+COLUMN\b",
    ]
    
    for pattern in destructive_patterns:
        matches = re.findall(pattern, file_content, re.IGNORECASE)
        if matches:
            findings.append({
                "rule_name": "DB_DESTRUCTIVE_CHANGE",
                "rule_category": "DB Impact Risk",
                "severity": "Critical",
                "risk_score": 90,
                "description": f"Destructive database operation detected in {file_path}",
                "recommendation": "Review destructive changes carefully and ensure backups exist.",
                "matched_pattern": str(matches[0]),
                "is_blocking": True
            })
            
    return findings

def execute_database_rules(file_content: str, file_path: str):
    findings = []
    findings.extend(check_destructive_db_operations(file_content, file_path))
    return findings

database_rules = [
    {
        "name": "Database Schema Rules",
        "category": "DB Impact Risk",
        "executor": execute_database_rules
    }
]
