import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = ROOT / "app"


def _module_names() -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for path in sorted(APP_ROOT.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        mapping[path.stem] = path
    return mapping


def _imported_modules(tree: ast.AST) -> set[str]:
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
    return {module for module in imports if module}


def test_ui_layer_does_not_bypass_services():
    ui_path = APP_ROOT / "ui" / "dashboard.py"
    tree = ast.parse(ui_path.read_text(encoding="utf-8"))
    imports = _imported_modules(tree)
    assert "app.validators" not in imports
    assert "app.rules" not in imports


def test_persistence_layer_does_not_import_ui():
    repo_path = APP_ROOT / "storage" / "sqlite_repo.py"
    tree = ast.parse(repo_path.read_text(encoding="utf-8"))
    imports = _imported_modules(tree)
    assert "app.ui" not in imports
