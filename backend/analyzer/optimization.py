def optimize_python_code(code: str):

    suggestions = []

    # ==========================================
    # 1. range(len()) optimization
    # ==========================================

    if "range(len(" in code:

        suggestions.append(
            "Consider iterating directly over the collection instead of using range(len())."
        )

    # ==========================================
    # 2. Manual maximum loop
    # ==========================================

    if (
        "max_value = numbers[0]" in code
        and "for number in numbers" in code
    ):

        suggestions.append(
            "Consider using Python's built-in max() function instead of a manual loop."
        )

    # ==========================================
    # 3. List append loop
    # ==========================================

    if (
        "result = []" in code
        and "result.append(" in code
        and "for " in code
    ):

        suggestions.append(
            "Consider using a list comprehension instead of repeatedly using append()."
        )

    # ==========================================
    # 4. Nested loops
    # ==========================================

    lines = code.splitlines()

    for i, line in enumerate(lines):

        if line.startswith("    for ") or line.startswith("        for "):

            suggestions.append(
                "Nested loops detected. Consider whether the algorithm can be optimized to reduce repeated iterations."
            )

            break

    # ==========================================
    # 5. No optimization
    # ==========================================

    if not suggestions:

        suggestions.append(
            "No obvious optimization opportunities detected."
        )

    return {
        "status": "success",
        "suggestions": suggestions
    }