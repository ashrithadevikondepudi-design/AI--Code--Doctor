import ast
import re
import io
import tokenize


# ============================================================
# 1. REMOVE UNNECESSARY SEMICOLONS
# ============================================================

def remove_semicolons(code: str):

    suggestions = []

    try:

        tokens = list(
            tokenize.generate_tokens(
                io.StringIO(code).readline
            )
        )

    except (
        tokenize.TokenError,
        IndentationError
    ):

        return code, []

    semicolons = []

    for token in tokens:

        if (
            token.type == tokenize.OP
            and token.string == ";"
        ):

            semicolons.append(token)

    if not semicolons:

        return code, []

    lines = code.splitlines(
        keepends=True
    )

    line_starts = []

    position = 0

    for line in lines:

        line_starts.append(position)

        position += len(line)

    def absolute_position(pos):

        line_number, column = pos

        return (
            line_starts[line_number - 1]
            + column
        )

    replacements = []

    for token in semicolons:

        start = absolute_position(
            token.start
        )

        end = absolute_position(
            token.end
        )

        line_number = token.start[0]

        current_line = lines[
            line_number - 1
        ]

        column = token.start[1]

        text_after = current_line[
            column + 1:
        ].strip()

        if (
            text_after == ""
            or text_after.startswith("#")
        ):

            replacements.append(
                (
                    start,
                    end,
                    ""
                )
            )

            suggestions.append(
                f"Removed unnecessary ';' "
                f"on line {line_number}."
            )

        else:

            indentation = (
                len(current_line)
                - len(
                    current_line.lstrip()
                )
            )

            replacement = (
                "\n"
                + (" " * indentation)
            )

            replacements.append(
                (
                    start,
                    end,
                    replacement
                )
            )

            suggestions.append(
                f"Replaced ';' with a new line "
                f"on line {line_number}."
            )

    improved_code = code

    for (
        start,
        end,
        replacement
    ) in reversed(replacements):

        improved_code = (
            improved_code[:start]
            + replacement
            + improved_code[end:]
        )

    return improved_code, suggestions


# ============================================================
# 2. FIX MISSING COLONS
# ============================================================

def try_fix_missing_colons(code: str):

    lines = code.splitlines()

    suggestions = []

    changed = False

    for index, line in enumerate(lines):

        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            continue

        if "#" in stripped:

            code_part, comment = (
                stripped.split("#", 1)
            )

            code_part = code_part.rstrip()

        else:

            code_part = stripped
            comment = None

        if code_part.endswith(":"):
            continue

        should_add_colon = False

        if re.match(
            r"^if\s+.+$",
            code_part
        ):

            should_add_colon = True

        elif re.match(
            r"^elif\s+.+$",
            code_part
        ):

            should_add_colon = True

        elif code_part == "else":

            should_add_colon = True

        elif re.match(
            r"^for\s+.+\s+in\s+.+$",
            code_part
        ):

            should_add_colon = True

        elif re.match(
            r"^while\s+.+$",
            code_part
        ):

            should_add_colon = True

        elif re.match(
            r"^def\s+[A-Za-z_][A-Za-z0-9_]*"
            r"\s*\(.*\)$",
            code_part
        ):

            should_add_colon = True

        elif re.match(
            r"^async\s+def\s+[A-Za-z_][A-Za-z0-9_]*"
            r"\s*\(.*\)$",
            code_part
        ):

            should_add_colon = True

        elif re.match(
            r"^class\s+[A-Za-z_][A-Za-z0-9_]*"
            r"(\s*\(.*\))?$",
            code_part
        ):

            should_add_colon = True

        elif code_part == "try":

            should_add_colon = True

        elif re.match(
            r"^except(\s+.+)?$",
            code_part
        ):

            should_add_colon = True

        elif code_part == "finally":

            should_add_colon = True

        elif re.match(
            r"^with\s+.+$",
            code_part
        ):

            should_add_colon = True

        elif re.match(
            r"^async\s+for\s+.+\s+in\s+.+$",
            code_part
        ):

            should_add_colon = True

        elif re.match(
            r"^async\s+with\s+.+$",
            code_part
        ):

            should_add_colon = True

        if should_add_colon:

            indentation = (
                len(line)
                - len(line.lstrip())
            )

            spaces = " " * indentation

            new_line = (
                spaces
                + code_part
                + ":"
            )

            if comment is not None:

                new_line += (
                    "  #"
                    + comment
                )

            lines[index] = new_line

            suggestions.append(
                f"Added missing ':' "
                f"on line {index + 1}."
            )

            changed = True

    if not changed:

        return code, []

    return (
        "\n".join(lines),
        suggestions
    )


# ============================================================
# 3. GET MODULE-LEVEL ASSIGNMENTS
# ============================================================

def get_module_assignments(tree):

    assignments = []

    for node in tree.body:

        if isinstance(
            node,
            ast.Assign
        ):

            for target in node.targets:

                if isinstance(
                    target,
                    ast.Name
                ):

                    assignments.append(
                        (
                            target.id,
                            node.lineno
                        )
                    )

        elif isinstance(
            node,
            ast.AnnAssign
        ):

            if isinstance(
                node.target,
                ast.Name
            ):

                assignments.append(
                    (
                        node.target.id,
                        node.lineno
                    )
                )

        elif isinstance(
            node,
            ast.AugAssign
        ):

            if isinstance(
                node.target,
                ast.Name
            ):

                assignments.append(
                    (
                        node.target.id,
                        node.lineno
                    )
                )

    return assignments


# ============================================================
# 4. FIX UNDEFINED VARIABLE IN print()
# ============================================================

def improve_undefined_print(
    code,
    tree,
    suggestions
):

    lines = code.splitlines()

    module_assignments = (
        get_module_assignments(tree)
    )

    for node in tree.body:

        if not isinstance(
            node,
            ast.Expr
        ):
            continue

        call = node.value

        if not isinstance(
            call,
            ast.Call
        ):
            continue

        if not isinstance(
            call.func,
            ast.Name
        ):
            continue

        if call.func.id != "print":
            continue

        if len(call.args) != 1:
            continue

        argument = call.args[0]

        if not isinstance(
            argument,
            ast.Name
        ):
            continue

        variable = argument.id

        candidates = [
            (name, line)
            for name, line
            in module_assignments
            if line < node.lineno
        ]

        if not candidates:
            continue

        if any(
            name == variable
            for name, _ in candidates
        ):
            continue

        candidate_name, _ = (
            candidates[-1]
        )

        line_index = node.lineno - 1

        original_line = lines[
            line_index
        ]

        old_text = (
            f"print({variable})"
        )

        new_text = (
            f"print({candidate_name})"
        )

        new_line = original_line.replace(
            old_text,
            new_text,
            1
        )

        if new_line != original_line:

            lines[line_index] = new_line

            suggestions.append(
                f"Replaced undefined variable "
                f"'{variable}' with the previously "
                f"assigned variable "
                f"'{candidate_name}'."
            )

            return "\n".join(lines)

    return code


# ============================================================
# 5. FIX =+ TO += / =- TO -=
# ============================================================
def fix_plus_assignment(
    code,
    tree,
    suggestions
):

    lines = code.splitlines()

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

            if child.value.operand.id != loop_variable:
                continue

            if len(child.targets) != 1:
                continue

            target = child.targets[0]

            if not isinstance(target, ast.Name):
                continue

            operator = "+" if isinstance(
                child.value.op,
                ast.UAdd
            ) else "-"

            line_index = child.lineno - 1

            if not (0 <= line_index < len(lines)):
                continue

            old_line = lines[line_index]

            pattern = (
                rf"(\b{re.escape(target.id)}\b)"
                rf"\s*=\s*"
                rf"({re.escape(operator)})"
                rf"\s*"
                rf"(\b{re.escape(loop_variable)}\b)"
            )

            replacement = rf"\1 {operator}= \3"

            new_line = re.sub(
                pattern,
                replacement,
                old_line,
                count=1
            )

            if new_line == old_line:
                continue

            lines[line_index] = new_line

            suggestions.append(
                f"Changed '{target.id} ={operator} "
                f"{loop_variable}' to "
                f"'{target.id} {operator}= "
                f"{loop_variable}'."
            )

            return "\n".join(lines)

    return code


# 6. FIX len(loop_variable)
# ============================================================

def fix_wrong_len_usage(
    code,
    tree,
    suggestions
):

    lines = code.splitlines()

    loop_variables = {}

    for node in ast.walk(tree):

        if not isinstance(
            node,
            ast.For
        ):
            continue

        if not isinstance(
            node.target,
            ast.Name
        ):
            continue

        if not isinstance(
            node.iter,
            ast.Name
        ):
            continue

        loop_variables[
            node.target.id
        ] = node.iter.id

    for node in ast.walk(tree):

        if not isinstance(
            node,
            ast.Call
        ):
            continue

        if not (
            isinstance(
                node.func,
                ast.Name
            )
            and node.func.id == "len"
        ):
            continue

        if len(node.args) != 1:
            continue

        argument = node.args[0]

        if not isinstance(
            argument,
            ast.Name
        ):
            continue

        loop_variable = argument.id

        if loop_variable not in loop_variables:
            continue

        collection = (
            loop_variables[
                loop_variable
            ]
        )

        line_index = node.lineno - 1

        if not (
            0 <= line_index < len(lines)
        ):
            continue

        old_text = (
            f"len({loop_variable})"
        )

        new_text = (
            f"len({collection})"
        )

        if old_text not in lines[
            line_index
        ]:
            continue

        lines[line_index] = (
            lines[line_index].replace(
                old_text,
                new_text,
                1
            )
        )

        suggestions.append(
            f"Changed {old_text} to "
            f"{new_text} because "
            f"'{loop_variable}' is the loop item."
        )

        return "\n".join(lines)

    return code


# ============================================================
# 7. RENAME sum VARIABLE TO total
# ============================================================

def rename_sum_variable(
    code,
    tree,
    suggestions
):

    lines = code.splitlines()

    sum_nodes = []

    for node in ast.walk(tree):

        if isinstance(
            node,
            ast.Name
        ):

            if node.id == "sum":

                sum_nodes.append(node)

    if not sum_nodes:
        return code

    changed = False

    for node in sum_nodes:

        line_index = node.lineno - 1

        if not (
            0 <= line_index < len(lines)
        ):
            continue

        line = lines[line_index]

        pattern = r"\bsum\b"

        new_line = re.sub(
            pattern,
            "total",
            line
        )

        if new_line != line:

            lines[line_index] = new_line
            changed = True

    if changed:

        suggestions.append(
            "Renamed variable 'sum' to "
            "'total' to avoid shadowing "
            "Python's built-in sum()."
        )

        return "\n".join(lines)

    return code


# ============================================================
# 8. STRING + NUMBER IN print()
# ============================================================

def fix_string_number_print(
    code,
    tree,
    suggestions
):

    lines = code.splitlines()
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

        if not isinstance(node, ast.Call):
            continue

        if not isinstance(node.func, ast.Name):
            continue

        if node.func.id != "print":
            continue

        if len(node.args) != 1:
            continue

        expression = node.args[0]

        if not isinstance(expression, ast.BinOp):
            continue

        if not isinstance(expression.op, ast.Add):
            continue

        left = expression.left
        right = expression.right

        left_string = (
            isinstance(left, ast.Constant)
            and isinstance(left.value, str)
        )

        right_string = (
            isinstance(right, ast.Constant)
            and isinstance(right.value, str)
        )

        left_number = (
            isinstance(left, ast.Constant)
            and isinstance(left.value, (int, float))
            and not isinstance(left.value, bool)
        ) or (
            isinstance(left, ast.Name)
            and left.id in numeric_names
        )

        right_number = (
            isinstance(right, ast.Constant)
            and isinstance(right.value, (int, float))
            and not isinstance(right.value, bool)
        ) or (
            isinstance(right, ast.Name)
            and right.id in numeric_names
        )

        if not (
            (left_string and right_number)
            or (right_string and left_number)
        ):
            continue

        line_index = node.lineno - 1

        if not (0 <= line_index < len(lines)):
            continue

        left_text = ast.get_source_segment(code, left)
        right_text = ast.get_source_segment(code, right)

        if not left_text or not right_text:
            continue

        old_expression = (
            f"{left_text} + {right_text}"
        )

        new_expression = (
            f"{left_text}, {right_text}"
        )

        new_line = lines[line_index].replace(
            old_expression,
            new_expression,
            1
        )

        if new_line == lines[line_index]:
            continue

        lines[line_index] = new_line

        suggestions.append(
            "Changed string + number "
            "concatenation to separate "
            "print arguments."
        )

        return "\n".join(lines)

    return code


# ============================================================
# 9. DICTIONARY BARE KEY
# ============================================================

def fix_dictionary_keys(
    code,
    tree,
    suggestions
):

    lines = code.splitlines()

    for node in ast.walk(tree):

        if not isinstance(
            node,
            ast.Dict
        ):
            continue

        for key in node.keys:

            if not isinstance(
                key,
                ast.Name
            ):
                continue

            line_index = key.lineno - 1

            if not (
                0 <= line_index < len(lines)
            ):
                continue

            key_name = key.id

            pattern = (
                rf"(?<!['\"])\b"
                rf"{re.escape(key_name)}"
                rf"\b(?!['\"])"
            )

            new_line = re.sub(
                pattern,
                f"'{key_name}'",
                lines[line_index],
                count=1
            )

            if new_line != lines[
                line_index
            ]:

                lines[line_index] = new_line

                suggestions.append(
                    f"Changed dictionary key "
                    f"'{key_name}' to "
                    f"'{key_name}' as a string."
                )

                return "\n".join(lines)

    return code


# ============================================================
# 10. STANDALONE == TO =
# ============================================================

def fix_comparison_as_statement(
    code,
    tree,
    suggestions
):

    lines = code.splitlines()

    for node in ast.walk(tree):

        if not isinstance(
            node,
            ast.Expr
        ):
            continue

        expression = node.value

        if not isinstance(
            expression,
            ast.Compare
        ):
            continue

        if len(expression.ops) != 1:
            continue

        if not isinstance(
            expression.ops[0],
            ast.Eq
        ):
            continue

        if not (
            isinstance(
                expression.left,
                ast.Name
            )
            and len(expression.comparators) == 1
            and isinstance(
                expression.comparators[0],
                ast.Name
            )
        ):
            continue

        left = (
            expression.left.id
        )

        right = (
            expression.comparators[0].id
        )

        line_index = node.lineno - 1

        if not (
            0 <= line_index < len(lines)
        ):
            continue

        old_line = lines[
            line_index
        ]

        pattern = (
            rf"\b{re.escape(left)}"
            rf"\s*==\s*"
            rf"{re.escape(right)}\b"
        )

        new_line = re.sub(
            pattern,
            f"{left} = {right}",
            old_line,
            count=1
        )

        if new_line != old_line:

            lines[line_index] = new_line

            suggestions.append(
                f"Changed standalone comparison "
                f"'{left} == {right}' to "
                f"assignment '{left} = {right}'."
            )

            return "\n".join(lines)

    return code


# ============================================================
# 11. APPEND LOOP -> LIST COMPREHENSION
# ============================================================

def improve_append_loop(
    code,
    tree,
    suggestions
):

    lines = code.splitlines()

    for node in tree.body:

        if not isinstance(
            node,
            ast.Assign
        ):
            continue

        if (
            len(node.targets) != 1
            or not isinstance(
                node.targets[0],
                ast.Name
            )
            or not isinstance(
                node.value,
                ast.List
            )
            or len(node.value.elts) != 0
        ):
            continue

        result_name = (
            node.targets[0].id
        )

        for candidate in tree.body:

            if not isinstance(
                candidate,
                ast.For
            ):
                continue

            if candidate.lineno <= (
                node.end_lineno
            ):
                continue

            if candidate.lineno != (
                node.end_lineno + 2
            ):
                continue

            if not isinstance(
                candidate.target,
                ast.Name
            ):
                continue

            if not isinstance(
                candidate.iter,
                ast.Name
            ):
                continue

            if len(candidate.body) != 1:
                continue

            loop_variable = (
                candidate.target.id
            )

            body = candidate.body[0]

            if not isinstance(
                body,
                ast.Expr
            ):
                continue

            call = body.value

            if not isinstance(
                call,
                ast.Call
            ):
                continue

            if not isinstance(
                call.func,
                ast.Attribute
            ):
                continue

            if call.func.attr != "append":
                continue

            if len(call.args) != 1:
                continue

            if not isinstance(
                call.func.value,
                ast.Name
            ):
                continue

            if call.func.value.id != result_name:
                continue

            value = call.args[0]

            if not isinstance(
                value,
                ast.Name
            ):
                continue

            if value.id != loop_variable:
                continue

            collection = (
                candidate.iter.id
            )

            indentation = (
                len(
                    lines[
                        node.lineno - 1
                    ]
                )
                - len(
                    lines[
                        node.lineno - 1
                    ].lstrip()
                )
            )

            spaces = " " * indentation

            new_line = (
                f"{spaces}{result_name} = "
                f"[{loop_variable} "
                f"for {loop_variable} "
                f"in {collection}]"
            )

            start = node.lineno - 1
            end = candidate.end_lineno

            lines[start:end] = [
                new_line
            ]

            suggestions.append(
                "Replaced a simple append loop "
                "with a list comprehension."
            )

            return "\n".join(lines)

    return code


# ============================================================
# 12. range(len()) -> DIRECT ITERATION
# ============================================================

def improve_range_len_loop(
    code,
    tree,
    suggestions
):

    lines = code.splitlines()

    for node in ast.walk(tree):

        if not isinstance(
            node,
            ast.For
        ):
            continue

        if not isinstance(
            node.target,
            ast.Name
        ):
            continue

        if not isinstance(
            node.iter,
            ast.Call
        ):
            continue

        if not isinstance(
            node.iter.func,
            ast.Name
        ):
            continue

        if node.iter.func.id != "range":
            continue

        if len(node.iter.args) != 1:
            continue

        length_call = (
            node.iter.args[0]
        )

        if not isinstance(
            length_call,
            ast.Call
        ):
            continue

        if not isinstance(
            length_call.func,
            ast.Name
        ):
            continue

        if length_call.func.id != "len":
            continue

        if len(length_call.args) != 1:
            continue

        collection = (
            length_call.args[0]
        )

        if not isinstance(
            collection,
            ast.Name
        ):
            continue

        if len(node.body) != 1:
            continue

        body = node.body[0]

        if not isinstance(
            body,
            ast.Expr
        ):
            continue

        call = body.value

        if not isinstance(
            call,
            ast.Call
        ):
            continue

        if not isinstance(
            call.func,
            ast.Name
        ):
            continue

        if call.func.id != "print":
            continue

        if len(call.args) != 1:
            continue

        argument = call.args[0]

        if not isinstance(
            argument,
            ast.Subscript
        ):
            continue

        if not isinstance(
            argument.value,
            ast.Name
        ):
            continue

        if argument.value.id != (
            collection.id
        ):
            continue

        index = argument.slice

        if not isinstance(
            index,
            ast.Name
        ):
            continue

        if index.id != (
            node.target.id
        ):
            continue

        indentation = (
            len(
                lines[
                    node.lineno - 1
                ]
            )
            - len(
                lines[
                    node.lineno - 1
                ].lstrip()
            )
        )

        spaces = " " * indentation

        new_lines = [
            (
                f"{spaces}for value "
                f"in {collection.id}:"
            ),
            (
                f"{spaces}    print(value)"
            )
        ]

        start = node.lineno - 1
        end = node.end_lineno

        lines[start:end] = new_lines

        suggestions.append(
            "Replaced range(len(...)) indexing "
            "with direct iteration."
        )

        return "\n".join(lines)

    return code


# ============================================================
# 13. REMOVE UNUSED VARIABLES
# ============================================================

def remove_unused_variables(
    code,
    tree,
    suggestions
):

    lines = code.splitlines()

    used_variables = set()

    for node in ast.walk(tree):

        if isinstance(
            node,
            ast.Name
        ):

            if isinstance(
                node.ctx,
                ast.Load
            ):

                used_variables.add(
                    node.id
                )

    for node in tree.body:

        if not isinstance(
            node,
            ast.Assign
        ):
            continue

        if len(node.targets) != 1:
            continue

        target = node.targets[0]

        if not isinstance(
            target,
            ast.Name
        ):
            continue

        variable_name = target.id

        if variable_name in (
            used_variables
        ):
            continue

        if variable_name.startswith("_"):
            continue

        if not isinstance(
            node.value,
            (
                ast.Constant,
                ast.List,
                ast.Tuple,
                ast.Set,
                ast.Dict
            )
        ):
            continue

        start = node.lineno - 1
        end = node.end_lineno

        del lines[start:end]

        suggestions.append(
            f"Removed unused variable "
            f"'{variable_name}'."
        )

        return "\n".join(lines)

    return code


# ============================================================
# 14. MAIN IMPROVEMENT FUNCTION
# ============================================================

def improve_python_code(code: str):

    original_code = code

    suggestions = []

    # --------------------------------------------------------
    # STEP 1: Semicolons
    # --------------------------------------------------------

    code, semicolon_suggestions = (
        remove_semicolons(code)
    )

    suggestions.extend(
        semicolon_suggestions
    )

    # --------------------------------------------------------
    # STEP 2: Missing colons
    # --------------------------------------------------------

    fixed_code, colon_suggestions = (
        try_fix_missing_colons(code)
    )

    if fixed_code != code:

        try:

            ast.parse(fixed_code)

            code = fixed_code

            suggestions.extend(
                colon_suggestions
            )

        except SyntaxError:
            pass

    # --------------------------------------------------------
    # STEP 3: Parse
    # --------------------------------------------------------

    try:

        tree = ast.parse(code)

    except SyntaxError as e:

        return {
            "status": "error",
            "original_code": original_code,
            "improved_code": code,
            "message": (
                "Cannot improve code because of "
                f"a syntax error: {e.msg}"
            ),
            "suggestions": suggestions
        }

    # --------------------------------------------------------
    # STEP 4: Fix undefined print
    # --------------------------------------------------------

    improved_code = (
        improve_undefined_print(
            code,
            tree,
            suggestions
        )
    )

    try:

        tree = ast.parse(
            improved_code
        )

    except SyntaxError:

        tree = ast.parse(code)

    # --------------------------------------------------------
    # STEP 5: Fix =+
    # --------------------------------------------------------

    improved_code = (
        fix_plus_assignment(
            improved_code,
            tree,
            suggestions
        )
    )

    try:

        tree = ast.parse(
            improved_code
        )

    except SyntaxError:

        tree = ast.parse(code)

    # --------------------------------------------------------
    # STEP 6: Fix wrong len()
    # --------------------------------------------------------

    improved_code = (
        fix_wrong_len_usage(
            improved_code,
            tree,
            suggestions
        )
    )

    try:

        tree = ast.parse(
            improved_code
        )

    except SyntaxError:

        tree = ast.parse(code)

    # --------------------------------------------------------
    # STEP 7: Rename sum -> total
    # --------------------------------------------------------

    improved_code = (
        rename_sum_variable(
            improved_code,
            tree,
            suggestions
        )
    )

    try:

        tree = ast.parse(
            improved_code
        )

    except SyntaxError:

        tree = ast.parse(code)

    # --------------------------------------------------------
    # STEP 8: Fix string + number
    # --------------------------------------------------------

    improved_code = (
        fix_string_number_print(
            improved_code,
            tree,
            suggestions
        )
    )

    try:

        tree = ast.parse(
            improved_code
        )

    except SyntaxError:

        tree = ast.parse(code)

    # --------------------------------------------------------
    # STEP 9: Fix dictionary keys
    # --------------------------------------------------------

    improved_code = (
        fix_dictionary_keys(
            improved_code,
            tree,
            suggestions
        )
    )

    try:

        tree = ast.parse(
            improved_code
        )

    except SyntaxError:

        tree = ast.parse(code)

    # --------------------------------------------------------
    # STEP 10: Fix standalone ==
    # --------------------------------------------------------

    improved_code = (
        fix_comparison_as_statement(
            improved_code,
            tree,
            suggestions
        )
    )

    try:

        tree = ast.parse(
            improved_code
        )

    except SyntaxError:

        tree = ast.parse(code)

    # --------------------------------------------------------
    # STEP 11: Append loop
    # --------------------------------------------------------

    improved_code = (
        improve_append_loop(
            improved_code,
            tree,
            suggestions
        )
    )

    try:

        tree = ast.parse(
            improved_code
        )

    except SyntaxError:

        tree = ast.parse(code)

    # --------------------------------------------------------
    # STEP 12: range(len())
    # --------------------------------------------------------

    improved_code = (
        improve_range_len_loop(
            improved_code,
            tree,
            suggestions
        )
    )

    try:

        tree = ast.parse(
            improved_code
        )

    except SyntaxError:

        tree = ast.parse(code)

    # --------------------------------------------------------
    # STEP 13: Unused variables
    # --------------------------------------------------------

    improved_code = (
        remove_unused_variables(
            improved_code,
            tree,
            suggestions
        )
    )

    # --------------------------------------------------------
    # STEP 14: Final result
    # --------------------------------------------------------

    if improved_code == original_code:

        return {
            "status": "no_changes",
            "original_code": original_code,
            "improved_code": original_code,
            "message": (
                "No safe automatic improvements found."
            ),
            "suggestions": []
        }

    return {
        "status": "success",
        "original_code": original_code,
        "improved_code": improved_code,
        "message": (
            "Code was improved successfully."
        ),
        "suggestions": suggestions
    }