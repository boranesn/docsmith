from pathlib import Path

from docsmith.models import DocCoverage, ParsedClass, ParsedFunction


def compute_coverage(
    functions: list[ParsedFunction],
    classes: list[ParsedClass],
) -> DocCoverage:
    public_fns = [f for f in functions if f.is_public]
    public_cls = [c for c in classes if c.is_public]

    all_symbols: list[tuple[str, str, bool]] = []  # (name, file, has_doc)
    for fn in public_fns:
        all_symbols.append((fn.name, fn.file_path, bool(fn.docstring)))
    for cls in public_cls:
        all_symbols.append((cls.name, cls.file_path, bool(cls.docstring)))
        for method in cls.methods:
            if method.is_public:
                all_symbols.append((method.name, method.file_path, bool(method.docstring)))

    total = len(all_symbols)
    documented = sum(1 for _, _, has_doc in all_symbols if has_doc)
    undocumented = [name for name, _, has_doc in all_symbols if not has_doc]
    pct = (documented / total * 100) if total > 0 else 0.0

    by_file: dict[str, list[bool]] = {}
    for name, fpath, has_doc in all_symbols:
        by_file.setdefault(fpath, []).append(has_doc)

    file_pct = {
        f: (sum(v) / len(v) * 100) for f, v in by_file.items() if v
    }

    return DocCoverage(
        total_public_symbols=total,
        documented_symbols=documented,
        coverage_pct=round(pct, 1),
        undocumented=undocumented,
        by_file=file_pct,
    )
