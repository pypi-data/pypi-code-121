import sys
import inspect
from typing import List, Callable, Tuple

from pynextflow.entities import Variable, Bash, Path, Val
from pynextflow.utils import _strip_indent, _indent, _join_lines


class Process:
    name: str
    directives: dict
    inputs: List
    outputs: List
    func: Callable
    args: List

    def __init__(self, func, args, directives: dict, inputs: List, outputs: List):
        self.name = str(func.__name__).upper()
        self.directives = directives if directives else {}
        self.inputs = inputs if inputs else []
        self.outputs = outputs if outputs else []
        self.func = func
        self.signature = inspect.signature(self.func)
        self.args = args

    def concat(self, b):
        return Operator("concat", self, [b])

    def collect(self):
        return Operator("collect", self, [])

    def _build_directives(self):
        directives = [f"{key} {repr(value)}" for key, value in self.directives.items()]
        return _join_lines(directives).strip() + "\n" if directives else ""

    def _build_input(self):
        return _strip_indent(f"""
            input:
                {_indent(_join_lines([repr(i) for i in self.inputs]), 4)}                
            """) + "\n" if self.inputs else ""

    def _build_output(self):
        return _strip_indent(f"""
            output:
                {_indent(_join_lines([repr(o) for o in self.outputs]), 4)}                
            """) + "\n" if self.outputs else ""

    def _build_script(self):
        return _strip_indent(f"""
                script:
                \"\"\"
                {_indent(self._build_script_body(), 4)}
                \"\"\"""")

    def _build_script_body(self):
        var_names = {k.name: Variable(k.name, dollar=True, quotes=self._use_quotes(k.annotation)) for k in self.signature.parameters.values()}
        if issubclass(self.signature.return_annotation, Bash):
            script = _join_lines(_strip_indent(self.func(**var_names)).strip().splitlines())
            return script

        code, deps = _get_source_code(self.func)
        code_import = []  # TODO ["pip install -q " + " ".join(["pynextflow"] + deps)]
        code_ini = code_import + ["/usr/bin/env python3 << EOF", "", "import pynextflow as nf"]

        code_args = ",".join([repr(v) for v in var_names.values()])
        code_end = [
            "",
            f"result = {self.func.__name__}({code_args})",
            "nf.pickle(result, 'return_result.pkl')",
            "", "EOF"
        ]
        return _join_lines(code_ini + code + code_end)

    @staticmethod
    def _use_quotes(annotation):
        if issubclass(annotation, str):
            return True
        if issubclass(annotation, Path):
            return True
        if issubclass(annotation, Val):
            return True
        return False

    def _pre_build(self):
        # Add results output
        if self.is_python():
            self.outputs.append(Path("'return_result.pkl'"))

    def is_python(self):
        return not issubclass(self.signature.return_annotation, Bash)

    def build(self):
        self._pre_build()
        script = self._build_script()
        return _strip_indent(f"""
                process {self.name} {{
                    {_indent(self._build_directives(), 5)}  
                    {_indent(self._build_input(), 5)}
                    {_indent(self._build_output(), 5)}                  
                    {_indent(script, 5)}
                }}
                """)


class Operator:
    name: str
    source: Process
    args: Tuple

    def __init__(self, name: str, source: Process, args):
        self.name = name
        self.source = source
        self.args = args

    def collect(self):
        return Operator("collect", self, [])


def _get_source_code(obj, key=None):

    if inspect.ismodule(obj):
        return [f"import {obj.__name__} as {key}"], [f"{obj.__name__}=={obj.__version__}"]

    closures = inspect.getclosurevars(obj)
    source_and_deps = [_get_source_code(v, key=k) for k, v in closures.globals.items()]
    code_globals = [line for lines, _ in source_and_deps for line in lines]
    code_globals.append("")
    deps = [d for _, dep in source_and_deps for d in dep]
    lines, _ = inspect.getsourcelines(obj)
    code_func = [line.rstrip() for line in lines if not line.startswith("@nf.")]

    return code_globals + code_func, deps
