import importlib

for module in ["black", "isort", "jinja2", "typer"]:
    try:
        importlib.import_module(module)
    except ModuleNotFoundError:
        raise ImportError(
            f"Cannot import '{module}', did you install the codegen dependencies? (pip install sila2[codegen])"
        )
