"""Tree-sitter based AST parser for Python and TypeScript source files."""

from pathlib import Path

from docsmith.ingestion.languages import detect_language
from docsmith.models import ParsedClass, ParsedFunction, Parameter


def parse_file(path: Path) -> tuple[list[ParsedFunction], list[ParsedClass]]:
    lang = detect_language(path)
    source = path.read_text(errors="replace")

    if lang == "python":
        return _parse_python(source, str(path))
    if lang in ("typescript", "javascript"):
        return _parse_typescript(source, str(path), lang)
    return [], []


# ── Python parser ──────────────────────────────────────────────────────────────

def _parse_python(source: str, file_path: str) -> tuple[list[ParsedFunction], list[ParsedClass]]:
    try:
        import tree_sitter_python as tspython
        from tree_sitter import Language, Parser

        PY_LANG = Language(tspython.language())
        parser = Parser(PY_LANG)
    except Exception:
        return _parse_python_fallback(source, file_path)

    tree = parser.parse(source.encode())
    functions: list[ParsedFunction] = []
    classes: list[ParsedClass] = []
    lines = source.splitlines()

    def get_text(node) -> str:  # type: ignore[no-untyped-def]
        return source[node.start_byte:node.end_byte]

    def extract_docstring(node) -> str | None:  # type: ignore[no-untyped-def]
        for child in node.children:
            if child.type == "block":
                for stmt in child.children:
                    if stmt.type == "expression_statement":
                        for s in stmt.children:
                            if s.type == "string":
                                raw = get_text(s)
                                return raw.strip('"""\'').strip()
        return None

    def extract_params(params_node) -> list[Parameter]:  # type: ignore[no-untyped-def]
        params: list[Parameter] = []
        for child in params_node.children:
            if child.type in ("identifier",):
                params.append(Parameter(name=get_text(child)))
            elif child.type == "typed_parameter":
                name = ""
                annotation = None
                for c in child.children:
                    if c.type == "identifier" and not name:
                        name = get_text(c)
                    elif c.type == "type":
                        annotation = get_text(c)
                if name:
                    params.append(Parameter(name=name, type_annotation=annotation))
        return params

    def visit(node, class_ctx: ParsedClass | None = None) -> None:  # type: ignore[no-untyped-def]
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            name = get_text(name_node) if name_node else "unknown"
            is_public = not name.startswith("_")
            params_node = node.child_by_field_name("parameters")
            params = extract_params(params_node) if params_node else []
            ret_node = node.child_by_field_name("return_type")
            ret_type = get_text(ret_node).lstrip("->").strip() if ret_node else None
            doc = extract_docstring(node)
            decorators = [
                get_text(c) for c in node.children if c.type == "decorator"
            ]
            sig = f"def {name}({', '.join(p.name for p in params)})"
            if ret_type:
                sig += f" -> {ret_type}"

            fn = ParsedFunction(
                name=name,
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                language="python",
                signature=sig,
                docstring=doc,
                parameters=params,
                return_type=ret_type,
                is_public=is_public,
                decorators=decorators,
            )
            if class_ctx:
                class_ctx.methods.append(fn)
            else:
                functions.append(fn)

        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            name = get_text(name_node) if name_node else "unknown"
            doc = extract_docstring(node)
            cls = ParsedClass(
                name=name,
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                language="python",
                docstring=doc,
                is_public=not name.startswith("_"),
            )
            for child in node.children:
                visit(child, class_ctx=cls)
            classes.append(cls)
            return

        for child in node.children:
            if node.type != "class_definition":
                visit(child)

    visit(tree.root_node)
    return functions, classes


def _parse_python_fallback(source: str, file_path: str) -> tuple[list[ParsedFunction], list[ParsedClass]]:
    """Regex-based fallback when tree-sitter is unavailable."""
    import ast

    functions: list[ParsedFunction] = []
    classes: list[ParsedClass] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return functions, classes

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            doc = ast.get_docstring(node)
            params = [
                Parameter(name=arg.arg, type_annotation=ast.unparse(arg.annotation) if arg.annotation else None)
                for arg in node.args.args
            ]
            ret = ast.unparse(node.returns) if node.returns else None
            sig = f"def {node.name}({', '.join(p.name for p in params)})"
            functions.append(ParsedFunction(
                name=node.name,
                file_path=file_path,
                line_start=node.lineno,
                line_end=node.end_lineno or node.lineno,
                language="python",
                signature=sig,
                docstring=doc,
                parameters=params,
                return_type=ret,
                is_public=not node.name.startswith("_"),
            ))
        elif isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node)
            classes.append(ParsedClass(
                name=node.name,
                file_path=file_path,
                line_start=node.lineno,
                line_end=node.end_lineno or node.lineno,
                language="python",
                docstring=doc,
                is_public=not node.name.startswith("_"),
            ))
    return functions, classes


# ── TypeScript / JavaScript parser ────────────────────────────────────────────

def _parse_typescript(source: str, file_path: str, lang: str) -> tuple[list[ParsedFunction], list[ParsedClass]]:
    try:
        from tree_sitter import Language, Parser
        if lang == "typescript":
            import tree_sitter_typescript as tsts
            TS_LANG = Language(tsts.language_typescript())
        else:
            import tree_sitter_javascript as tsjs
            TS_LANG = Language(tsjs.language())
        parser = Parser(TS_LANG)
    except Exception:
        return [], []

    tree = parser.parse(source.encode())
    functions: list[ParsedFunction] = []
    classes: list[ParsedClass] = []

    def get_text(node) -> str:  # type: ignore[no-untyped-def]
        return source[node.start_byte:node.end_byte]

    def visit(node) -> None:  # type: ignore[no-untyped-def]
        if node.type in ("function_declaration", "function"):
            name_node = node.child_by_field_name("name")
            name = get_text(name_node) if name_node else "anonymous"
            fn = ParsedFunction(
                name=name,
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                language=lang,
                signature=f"function {name}()",
                is_public=True,
            )
            functions.append(fn)

        elif node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            name = get_text(name_node) if name_node else "AnonymousClass"
            cls = ParsedClass(
                name=name,
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                language=lang,
            )
            classes.append(cls)

        for child in node.children:
            visit(child)

    visit(tree.root_node)
    return functions, classes
