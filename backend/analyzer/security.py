import ast


def analyze_security(code: str):

    issues = []

    try:
        tree = ast.parse(code)

    except SyntaxError:
        return {
            "status": "error",
            "issues": [
                "Cannot perform security analysis because the code contains a syntax error."
            ]
        }

    for node in ast.walk(tree):

        # Dangerous eval()
        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                if node.func.id == "eval":

                    issues.append({
                        "type": "Security Risk",
                        "message": "Avoid eval() when possible because it can execute arbitrary code.",
                        "line": node.lineno
                    })

                # Dangerous exec()
                if node.func.id == "exec":

                    issues.append({
                        "type": "Security Risk",
                        "message": "Avoid exec() when possible because it can execute arbitrary code.",
                        "line": node.lineno
                    })

        # Hard-coded passwords
        if isinstance(node, ast.Assign):

            for target in node.targets:

                if isinstance(target, ast.Name):

                    variable_name = target.id.lower()

                    if any(word in variable_name for word in [
                        "password",
                        "passwd",
                        "secret",
                        "api_key",
                        "apikey"
                    ]):

                        issues.append({
                            "type": "Security Risk",
                            "message": "Possible hard-coded secret detected. Use environment variables or a secret manager.",
                            "line": node.lineno
                        })

    if not issues:

        return {
            "status": "secure",
            "message": "No obvious security risks detected."
        }

    return {
        "status": "issues_found",
        "issues": issues
    }