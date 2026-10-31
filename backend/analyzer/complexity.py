import ast


def complexity_analysis(code: str):

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "status": "error",
            "message": "Cannot analyze complexity because the code contains a syntax error."
        }

    loop_count = 0
    max_loop_depth = 0

    def visit(node, depth=0):

        nonlocal loop_count
        nonlocal max_loop_depth

        if isinstance(node, (ast.For, ast.While)):
            loop_count += 1
            depth += 1

            max_loop_depth = max(
                max_loop_depth,
                depth
            )

        for child in ast.iter_child_nodes(node):
            visit(child, depth)

    visit(tree)

    # -----------------------------
    # TIME COMPLEXITY
    # -----------------------------

    if max_loop_depth == 0:
        time_complexity = "O(1)"

    elif max_loop_depth == 1:
        time_complexity = "O(n)"

    elif max_loop_depth == 2:
        time_complexity = "O(n²)"

    else:
        time_complexity = f"O(n^{max_loop_depth})"

    # -----------------------------
    # SPACE COMPLEXITY
    # -----------------------------

    # Loops alone do not require
    # additional O(n) memory.
    space_complexity = "O(1)"

    return {
        "status": "success",
        "time_complexity": time_complexity,
        "space_complexity": space_complexity,
        "loop_depth": max_loop_depth
    }