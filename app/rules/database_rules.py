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

def check_missing_where_clause(file_content: str, file_path: str):
    findings = []
    lines = file_content.splitlines()
    for line in lines:
        if re.search(r'\b(UPDATE|DELETE)\b', line, re.IGNORECASE) and not re.search(r'\bWHERE\b', line, re.IGNORECASE):
            findings.append({
                "rule_name": "DB_MISSING_WHERE",
                "rule_category": "DB Impact Risk",
                "severity": "High",
                "risk_score": 75,
                "description": f"Missing WHERE clause in {file_path}",
                "recommendation": "Ensure UPDATE/DELETE statements have a WHERE clause.",
                "matched_pattern": line.strip(),
                "is_blocking": False
            })
    return findings

def check_select_star(file_content: str, file_path: str):
    findings = []
    matches = re.findall(r'\bSELECT\s+\*\s+FROM\b', file_content, re.IGNORECASE)
    if matches:
        findings.append({
            "rule_name": "DB_SELECT_STAR",
            "rule_category": "DB Impact Risk",
            "severity": "Low",
            "risk_score": 20,
            "description": f"SELECT * detected in {file_path}",
            "recommendation": "Specify columns explicitly instead of using SELECT *.",
            "matched_pattern": str(matches[0]),
            "is_blocking": False
        })
    return findings

def check_large_index_creation(file_content: str, file_path: str):
    findings = []
    lines = file_content.splitlines()
    for line in lines:
        if re.search(r'\bCREATE\s+INDEX\b', line, re.IGNORECASE) and not re.search(r'\bCONCURRENTLY\b', line, re.IGNORECASE):
            findings.append({
                "rule_name": "DB_LARGE_INDEX",
                "rule_category": "DB Impact Risk",
                "severity": "Medium",
                "risk_score": 50,
                "description": f"Index creation without CONCURRENTLY in {file_path}",
                "recommendation": "Use CREATE INDEX CONCURRENTLY to avoid locking.",
                "matched_pattern": line.strip(),
                "is_blocking": False
            })
    return findings

def execute_database_rules(file_content: str, file_path: str):
    findings = []
    findings.extend(check_destructive_db_operations(file_content, file_path))
    findings.extend(check_missing_where_clause(file_content, file_path))
    findings.extend(check_select_star(file_content, file_path))
    findings.extend(check_large_index_creation(file_content, file_path))
    return findings

database_rules = [
    {
        "name": "Database Schema Rules",
        "category": "DB Impact Risk",
        "executor": execute_database_rules
    }
]
