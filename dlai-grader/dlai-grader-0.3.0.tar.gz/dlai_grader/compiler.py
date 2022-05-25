import ast
import sys
from types import ModuleType
from contextlib import nullcontext
from .io import suppress_stdout_stderr


def compile_module(
    code_as_str: str,
    module_name: str,
    wipe_global_state: bool = False,
    verbose: bool = True,
) -> ModuleType:
    """Compiles the string representation of some code and returns a compiled module.
    Args:
        code_as_str (str): Code represented as string.
        module_name (str): Name of the module.
        wipe_global_state (bool): If true then no global state is compiled. Defaults to False.
        verbose (bool): Whether to print out streams as a result of compilation. Defaults to True.
    Returns:
        ModuleType: The actual module that can be used to call functions/variables/etc.
    """
    code_ast = ast.parse(code_as_str)

    if wipe_global_state:
        for node in code_ast.body[:]:
            if not isinstance(
                node, (ast.FunctionDef, ast.Import, ast.ImportFrom, ast.ClassDef)
            ):
                code_ast.body.remove(node)

    with nullcontext() if verbose else suppress_stdout_stderr():
        module = ModuleType(module_name)
        code = compile(code_ast, f"{module_name}.py", "exec")
        sys.modules[module_name] = module
        exec(code, module.__dict__)
        return module
