import ast
import io
import tokenize


# ============================================================
# BUILT-IN PYTHON NAMES
# ============================================================

BUILTIN_NAMES = {
    "print",
    "input",
    "len",
    "range",
    "int",
    "float",
    "str",
    "list",
    "dict",
    "set",
    "tuple",
    "sum",
    "max",
    "min",
    "abs",
    "open",
    "enumerate",
    "zip",
    "map",
    "filter",
    "sorted",
    "reversed",
    "True",
    "False",
    "None",
    "bool",
    "bytes",
    "complex",
    "object",
    "type",
    "isinstance",
    "issubclass",
    "super",
    "Exception",
    "ValueError",
    "TypeError",
    "IndexError",
    "KeyError",
    "RuntimeError",
}


# ============================================================
# GET ASSIGNMENT TARGET NAMES
# ============================================================

def get_target_names(target):

    names = set()

    if isinstance(target, ast.Name):

        names.add(target.id)

    elif isinstance(
        target,
        (ast.Tuple, ast.List)
    ):

        for element in target.elts:

            names.update(
                get_target_names(element)
            )

    return names


# ============================================================
# GET DEFINED NAMES
# ============================================================

def get_defined_names(nodes):

    defined = set()

    for node in nodes:

        # x = 10
        if isinstance(node, ast.Assign):

            for target in node.targets:

                defined.update(
                    get_target_names(target)
                )

        # x: int = 10
        elif isinstance(
            node,
            ast.AnnAssign
        ):

            defined.update(
                get_target_names(
                    node.target
                )
            )

        # x += 1
        elif isinstance(
            node,
            ast.AugAssign
        ):

            defined.update(
                get_target_names(
                    node.target
                )
            )

        # for x in values
        elif isinstance(
            node,
            (ast.For, ast.AsyncFor)
        ):

            defined.update(
                get_target_names(
                    node.target
                )
            )

        # with open(...) as file
        elif isinstance(
            node,
            (ast.With, ast.AsyncWith)
        ):

            for item in node.items:

                if item.optional_vars:

                    defined.update(
                        get_target_names(
                            item.optional_vars
                        )
                    )

        # def function()
        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef
            )
        ):

            defined.add(node.name)

        # class MyClass
        elif isinstance(
            node,
            ast.ClassDef
        ):

            defined.add(node.name)

        # import math
        elif isinstance(
            node,
            ast.Import
        ):

            for alias in node.names:

                defined.add(
                    alias.asname
                    or alias.name.split(".")[0]
                )

        # from math import sqrt
        elif isinstance(
            node,
            ast.ImportFrom
        ):

            for alias in node.names:

                if alias.name != "*":

                    defined.add(
                        alias.asname
                        or alias.name
                    )

    return defined


# ============================================================
# CHECK A SCOPE
# ============================================================

def check_scope(
    node,
    available_names,
    issues
):

    # --------------------------------------------------------
    # Function scope
    # --------------------------------------------------------

    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef
        )
    ):

        local_names = set(
            available_names
        )

        # Normal arguments
        for arg in (
            node.args.posonlyargs
            + node.args.args
            + node.args.kwonlyargs
        ):

            local_names.add(arg.arg)

        # *args
        if node.args.vararg:

            local_names.add(
                node.args.vararg.arg
            )

        # **kwargs
        if node.args.kwarg:

            local_names.add(
                node.args.kwarg.arg
            )

        # Variables defined inside function
        local_names.update(
            get_defined_names(node.body)
        )

        # Check function body
        for child in node.body:

            check_node(
                child,
                local_names,
                issues
            )

        return

    # --------------------------------------------------------
    # Normal scope
    # --------------------------------------------------------

    for child in getattr(
        node,
        "body",
        []
    ):

        check_node(
            child,
            available_names,
            issues
        )


# ============================================================
# CHECK AST NODE FOR UNDEFINED NAMES
# ============================================================

def check_node(
    node,
    available_names,
    issues
):

    # --------------------------------------------------------
    # Function
    # --------------------------------------------------------

    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef
        )
    ):

        check_scope(
            node,
            available_names,
            issues
        )

        return

    # --------------------------------------------------------
    # Class
    # --------------------------------------------------------

    if isinstance(
        node,
        ast.ClassDef
    ):

        class_names = set(
            available_names
        )

        class_names.update(
            get_defined_names(
                node.body
            )
        )

        for child in node.body:

            check_node(
                child,
                class_names,
                issues
            )

        return

    # --------------------------------------------------------
    # Variable usage
    # --------------------------------------------------------

    if isinstance(
        node,
        ast.Name
    ):

        if isinstance(
            node.ctx,
            ast.Load
        ):

            name = node.id

            if name not in available_names:

                issues.append({
                    "type": "Possible Name Error",
                    "message": (
                        f"Variable '{name}' may be "
                        "used before it is defined."
                    ),
                    "line": node.lineno
                })

                # Don't report the same Name node
                # again while walking children.
                return

    # --------------------------------------------------------
    # Continue checking children
    # --------------------------------------------------------

    for child in ast.iter_child_nodes(node):

        check_node(
            child,
            available_names,
            issues
        )


# ============================================================
# CHECK SEMICOLONS
# ============================================================

def check_semicolons(code: str):

    issues = []

    try:

        tokens = tokenize.generate_tokens(
            io.StringIO(code).readline
        )

        for token in tokens:

            # IMPORTANT:
            #
            # A semicolon inside:
            #
            # "Hello; World"
            #
            # is part of a STRING token.
            #
            # It will NOT be detected here.
            #
            # Only an actual Python ; operator
            # has token.type == tokenize.OP.

            if (
                token.type == tokenize.OP
                and token.string == ";"
            ):

                issues.append({
                    "type": "Code Style",
                    "message": (
                        "Unnecessary semicolon ';' "
                        "detected."
                    ),
                    "line": token.start[0]
                })

    except (
        tokenize.TokenError,
        IndentationError
    ):

        pass

    return issues


# ============================================================
# CHECK NESTED LOOPS
# ============================================================

def check_nested_loops(
    tree,
    issues
):

    for node in ast.walk(tree):

        if not isinstance(
            node,
            (
                ast.For,
                ast.While
            )
        ):
            continue

        for child in ast.walk(node):

            if child is node:
                continue

            if isinstance(
                child,
                (
                    ast.For,
                    ast.While
                )
            ):

                issues.append({
                    "type": "Optimization",
                    "message": (
                        "Nested loops detected. "
                        "Check whether the algorithm "
                        "can be optimized."
                    ),
                    "line": child.lineno
                })

                break


# ============================================================
# CHECK =+ / =- OPERATOR MISTAKES
# ============================================================

def check_plus_assignment(tree):

    issues = []

    for node in ast.walk(tree):

        if not isinstance(node, ast.For):
            continue

        if not isinstance(node.target, ast.Name):
            continue

        loop_variable = node.target.id

        for child in ast.walk(node):

            if not isinstance(child, ast.Assign):
                continue

            if not isinstance(child.value, ast.UnaryOp):
                continue

            if not isinstance(
                child.value.op,
                (ast.UAdd, ast.USub)
            ):
                continue

            if not isinstance(child.value.operand, ast.Name):
                continue

            if len(child.targets) != 1:
                continue

            target = child.targets[0]

            if not isinstance(target, ast.Name):
                continue

            if child.value.operand.id != loop_variable:
                continue

            operator = "+" if isinstance(
                child.value.op,
                ast.UAdd
            ) else "-"

            issues.append({
                "type": "Logic Error",
                "message": (
                    f"'{target.id} ={operator} "
                    f"{loop_variable}' looks like a typo. "
                    f"Did you mean '{target.id} "
                    f"{operator}= {loop_variable}'?"
                ),
                "line": child.lineno
            })

    return issues


# ============================================================
# CHECK len(loop_variable)
# ============================================================

def check_wrong_len_usage(tree):

    issues = []
    loop_variables = {}

    for node in ast.walk(tree):

        if not isinstance(node, ast.For):
            continue

        if not isinstance(node.target, ast.Name):
            continue

        if not isinstance(node.iter, ast.Name):
            continue

        loop_variables[node.target.id] = node.iter.id

    for node in ast.walk(tree):

        if not isinstance(node, ast.Call):
            continue

        if not (
            isinstance(node.func, ast.Name)
            and node.func.id == "len"
        ):
            continue

        if len(node.args) != 1:
            continue

        argument = node.args[0]

        if not isinstance(argument, ast.Name):
            continue

        if argument.id not in loop_variables:
            continue

        collection = loop_variables[argument.id]

        issues.append({
            "type": "Logic Error",
            "message": (
                f"len({argument.id}) uses the loop item. "
                f"Did you mean len({collection})?"
            ),
            "line": node.lineno
        })

    return issues


# ============================================================
# CHECK STRING + NUMBER CONCATENATION
# ============================================================

def check_string_number_concatenation(code, tree):

    issues = []
    numeric_names = set()

    for node in ast.walk(tree):

        if isinstance(node, ast.Assign):

            if isinstance(node.value, ast.Constant):

                if (
                    isinstance(node.value.value, (int, float))
                    and not isinstance(node.value.value, bool)
                ):

                    for target in node.targets:

                        if isinstance(target, ast.Name):
                            numeric_names.add(target.id)

    for node in ast.walk(tree):

        if not isinstance(node, ast.BinOp):
            continue

        if not isinstance(node.op, ast.Add):
            continue

        left_string = (
            isinstance(node.left, ast.Constant)
            and isinstance(node.left.value, str)
        )

        right_string = (
            isinstance(node.right, ast.Constant)
            and isinstance(node.right.value, str)
        )

        left_number = (
            isinstance(node.left, ast.Constant)
            and isinstance(node.left.value, (int, float))
            and not isinstance(node.left.value, bool)
        ) or (
            isinstance(node.left, ast.Name)
            and node.left.id in numeric_names
        )

        right_number = (
            isinstance(node.right, ast.Constant)
            and isinstance(node.right.value, (int, float))
            and not isinstance(node.right.value, bool)
        ) or (
            isinstance(node.right, ast.Name)
            and node.right.id in numeric_names
        )

        if not (
            (left_string and right_number)
            or (right_string and left_number)
        ):
            continue

        issues.append({
            "type": "Type Error",
            "message": (
                "String and number values cannot be "
                "concatenated with '+'. Use separate "
                "print arguments or convert the number."
            ),
            "line": node.lineno
        })

    return issues


# ============================================================
# CHECK BARE DICTIONARY KEYS
# ============================================================

def check_dictionary_keys(tree):

    issues = []

    for node in ast.walk(tree):

        if not isinstance(node, ast.Dict):
            continue

        for key in node.keys:

            if not isinstance(key, ast.Name):
                continue

            issues.append({
                "type": "Code Style",
                "message": (
                    f"Dictionary key '{key.id}' is an "
                    "unquoted variable name. If this is "
                    "intended to be text, use a string key."
                ),
                "line": key.lineno
            })

    return issues


# ============================================================
# CHECK STANDALONE ==
# ============================================================

def check_comparison_as_statement(tree):

    issues = []

    for node in ast.walk(tree):

        if not isinstance(node, ast.Expr):
            continue

        expression = node.value

        if not isinstance(expression, ast.Compare):
            continue

        if len(expression.ops) != 1:
            continue

        if not isinstance(expression.ops[0], ast.Eq):
            continue

        if not (
            isinstance(expression.left, ast.Name)
            and len(expression.comparators) == 1
            and isinstance(expression.comparators[0], ast.Name)
        ):
            continue

        left = expression.left.id
        right = expression.comparators[0].id

        issues.append({
            "type": "Logic Error",
            "message": (
                f"Standalone '{left} == {right}' is a "
                f"comparison whose result is ignored. "
                f"If assignment was intended, use '{left} = {right}'."
            ),
            "line": node.lineno
        })

    return issues


# ============================================================
# MAIN REVIEW FUNCTION
# ============================================================

def review_python_code(code: str):

    issues = []

    # ========================================================
    # 1. SYNTAX CHECK
    # ========================================================

    try:

        tree = ast.parse(code)

    except SyntaxError as e:

        issues.append({
            "type": "Syntax Error",
            "message": e.msg,
            "line": e.lineno
        })

        return {
            "status": "issues_found",
            "issues": issues
        }

    # ========================================================
    # 2. FIND GLOBAL NAMES
    # ========================================================

    global_names = set(
        BUILTIN_NAMES
    )

    global_names.update(
        get_defined_names(
            tree.body
        )
    )

    # ========================================================
    # 3. CHECK UNDEFINED VARIABLES
    # ========================================================

    for node in tree.body:

        check_node(
            node,
            global_names,
            issues
        )

    # ========================================================
    # 4. CHECK SEMICOLONS
    # ========================================================

    semicolon_issues = check_semicolons(
        code
    )

    issues.extend(
        semicolon_issues
    )

    # ========================================================
    # 5. CHECK NESTED LOOPS
    # ========================================================

    check_nested_loops(
        tree,
        issues
    )

    # ========================================================
    # 6. CHECK OPERATOR / TYPE / COLLECTION ISSUES
    # ========================================================

    issues.extend(check_plus_assignment(tree))
    issues.extend(check_wrong_len_usage(tree))
    issues.extend(check_string_number_concatenation(code, tree))
    issues.extend(check_dictionary_keys(tree))
    issues.extend(check_comparison_as_statement(tree))

    # ========================================================
    # 6. REMOVE DUPLICATE ISSUES
    # ========================================================

    unique_issues = []

    seen = set()

    for issue in issues:

        key = (
            issue["type"],
            issue["message"],
            issue["line"]
        )

        if key not in seen:

            seen.add(key)

            unique_issues.append(
                issue
            )

    # ========================================================
    # 7. FINAL RESULT
    # ========================================================

    if not unique_issues:

        return {
            "status": "good",
            "message": (
                "No obvious issues detected. "
                "Code can still be reviewed for "
                "optimization and maintainability."
            ),
            "issues": []
        }

    return {
        "status": "issues_found",
        "issues": unique_issues
    }