import re



def check_sql_injection_risk(
    file_content: str,
    file_path: str
):

    findings = []


    patterns = [

        r"execute\(.*\+.*\)",

        r"SELECT .* \+",

        r"INSERT .* \+",

        r"UPDATE .* \+"

    ]


    for pattern in patterns:


        if re.search(
            pattern,
            file_content,
            re.IGNORECASE
        ):


            findings.append(

                {

                    "rule_name":
                        "Potential SQL Injection",


                    "rule_category":
                        "Code Quality",


                    "severity":
                        "Critical",


                    "risk_score":
                        90,


                    "description":
                        f"Dynamic SQL construction detected in {file_path}",


                    "recommendation":
                        "Use parameterized queries or ORM frameworks",


                    "matched_pattern":
                        pattern,


                    "is_blocking":
                        True

                }

            )


    return findings





def check_hardcoded_urls(
    file_content: str,
    file_path: str
):

    findings = []


    pattern = (

        r"https?://[^\s\"']+"

    )


    matches = re.findall(

        pattern,

        file_content

    )


    if matches:


        findings.append(

            {

                "rule_name":
                    "Hardcoded External URL",


                "rule_category":
                    "Code Quality",


                "severity":
                    "Low",


                "risk_score":
                    30,


                "description":
                    f"Hardcoded URL detected in {file_path}",


                "recommendation":
                    "Move environment specific URLs to configuration files",


                "matched_pattern":
                    str(matches),


                "is_blocking":
                    False

            }

        )


    return findings





def check_debug_statements(
    file_content: str,
    file_path: str
):

    findings = []


    patterns = [

        "print(",

        "console.log",

        "debugger",

        "System.out.println"

    ]


    for pattern in patterns:


        if pattern in file_content:


            findings.append(

                {

                    "rule_name":
                        "Debug Code In Application",


                    "rule_category":
                        "Code Quality",


                    "severity":
                        "Medium",


                    "risk_score":
                        45,


                    "description":
                        f"Debug statements found in {file_path}",


                    "recommendation":
                        "Remove debug statements before production release",


                    "matched_pattern":
                        pattern,


                    "is_blocking":
                        False

                }

            )


    return findings





def check_todo_fixme(
    file_content: str,
    file_path: str
):

    findings = []


    patterns = [

        "TODO",

        "FIXME",

        "HACK"

    ]


    for pattern in patterns:


        if pattern in file_content.upper():


            findings.append(

                {

                    "rule_name":
                        "Incomplete Code Marker",


                    "rule_category":
                        "Code Quality",


                    "severity":
                        "Low",


                    "risk_score":
                        20,


                    "description":
                        f"{pattern} marker found in {file_path}",


                    "recommendation":
                        "Resolve pending implementation items",


                    "matched_pattern":
                        pattern,


                    "is_blocking":
                        False

                }

            )


    return findings





def check_empty_exception_handling(
    file_content: str,
    file_path: str
):

    findings = []


    patterns = [

        "except:",

        "catch(Exception",

        "catch (Exception"

    ]


    for pattern in patterns:


        if pattern in file_content:


            findings.append(

                {

                    "rule_name":
                        "Exception Handling Risk",


                    "rule_category":
                        "Code Quality",


                    "severity":
                        "High",


                    "risk_score":
                        70,


                    "description":
                        f"Broad exception handling detected in {file_path}",


                    "recommendation":
                        "Handle specific exceptions and add proper logging",


                    "matched_pattern":
                        pattern,


                    "is_blocking":
                        False

                }

            )


    return findings





def check_weak_crypto(
    file_content: str,
    file_path: str
):

    findings = []


    weak_algorithms = [

        "MD5",

        "SHA1",

        "DES",

        "RC4"

    ]


    for algorithm in weak_algorithms:


        if algorithm in file_content:


            findings.append(

                {

                    "rule_name":
                        "Weak Cryptography Usage",


                    "rule_category":
                        "Security",


                    "severity":
                        "High",


                    "risk_score":
                        75,


                    "description":
                        f"Weak cryptographic algorithm {algorithm} used in {file_path}",


                    "recommendation":
                        "Use modern cryptographic algorithms like SHA-256 or AES",


                    "matched_pattern":
                        algorithm,


                    "is_blocking":
                        False

                }

            )


    return findings





def check_large_code_complexity(
    file_content: str,
    file_path: str
):

    findings = []


    line_count = len(

        file_content.splitlines()

    )


    if line_count > 1000:


        findings.append(

            {

                "rule_name":
                    "Large Source File Complexity",


                "rule_category":
                    "Code Quality",


                "severity":
                    "Medium",


                "risk_score":
                    50,


                "description":
                    f"Large source file detected ({line_count} lines)",


                "recommendation":
                    "Split large files into smaller maintainable components",


                "matched_pattern":
                    f"{line_count} lines",


                "is_blocking":
                    False

            }

        )


    return findings





def execute_coding_rules(
    file_content: str,
    file_path: str
):

    findings = []


    findings.extend(

        check_sql_injection_risk(

            file_content,

            file_path

        )

    )


    findings.extend(

        check_hardcoded_urls(

            file_content,

            file_path

        )

    )


    findings.extend(

        check_debug_statements(

            file_content,

            file_path

        )

    )


    findings.extend(

        check_todo_fixme(

            file_content,

            file_path

        )

    )


    findings.extend(

        check_empty_exception_handling(

            file_content,

            file_path

        )

    )


    findings.extend(

        check_weak_crypto(

            file_content,

            file_path

        )

    )


    findings.extend(

        check_large_code_complexity(

            file_content,

            file_path

        )

    )


    return findings





coding_rules = [

    {

        "name":
            "Application Code Risk Rules",


        "category":
            "Code Quality",


        "executor":
            execute_coding_rules

    }

]