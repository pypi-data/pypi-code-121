import inspect
import sys
from typing import List, Tuple as TTuple, Union

from pynextflow.entities.process import Process, Operator
from pynextflow.entities import Variable
from pynextflow.entities.workflow import Workflow
from pynextflow.executors import _get_executor, _executor_start, _executor_end, _executor_started
from pynextflow.utils import _strip_indent, _join_lines, _indent


def _workflow_decorator(_func=None):
    def decorator_workflow(func):
        def inner(*args, **kwargs):
            is_inner_workflow = _executor_started()
            if not is_inner_workflow:
                _executor_start()
            sig = inspect.signature(func)
            func_name = str(func.__name__).upper()
            var_names = [Variable(p) for p in sig.parameters]

            # take
            take_body = _strip_indent(
                f"""
                take:
                    {_join_lines([str(v) for v in var_names], indent=5)}
                """
            ) + "\n" if var_names else ""

            # main
            result = func(*var_names)
            processes, main, emit = _process_parser(result)
            main_body = _strip_indent(
                f"""
                main:
                    {_join_lines([str(m) for m in main], indent=5)}
                """
            ) + "\n"

            # emit
            emit_body = _strip_indent(
                f"""
                emit:
                    {_indent(emit, 5)}
                """
            ) + "\n" if emit else ""

            # workflow
            workflow_body = _strip_indent(
                f"""
                workflow {func_name} {{
                    {_indent(take_body, 5)}
                    {_indent(main_body, 5)}
                    {_indent(emit_body, 5)}
                }}
                """
            )

            w = Workflow(func_name, processes, workflow_body, args, func)

            if is_inner_workflow:
                return w

            _executor_end()
            executor = _get_executor()
            return executor.run(w)

        return inner

    if _func is None:
        return decorator_workflow
    else:
        return decorator_workflow(_func)


# Returns processes, main, emit
def _process_parser(node) -> TTuple[List[Union[Process, Workflow]], List[str], str]:
    if isinstance(node, Process) or isinstance(node, Workflow):
        r = [_process_parser(a) for a in node.args]
        p = [p for a, _, _ in r for p in a]
        m = [m for _, b, _ in r for m in b]
        arg_outs = ", ".join([_arg_to_out(a) for a in node.args])
        return p + [node], m + [f"{node.name}({arg_outs})"], f"{node.name}.out"

    if isinstance(node, Operator):
        src_p, src_m, src_e = _process_parser(node.source)
        r = [_process_parser(a) for a in node.args] if node.args else []
        p = [p for a, _, _ in r for p in a]
        m = [m for _, b, _ in r for m in b]
        e = [c for _, _, c in r]
        str_e = ", ".join(e)
        return p + src_p, src_m + m, f"{src_e}.{node.name}({str_e})"

    return [], [], ""


def _arg_to_out(arg) -> str:
    if isinstance(arg, Process) or isinstance(arg, Workflow):
        return f"{arg.name}.out"
    if isinstance(arg, str):
        return f"\"{arg}\""
    return str(arg)


def _print_bodies(a, file=sys.stdout):
    if isinstance(a, Process):
        print(a.build(), file=file)
        print("", file=file)
    if isinstance(a, Workflow):
        for p in a.processes:
            _print_bodies(p, file=file)
        print(a.body, file=file)
        print("", file=file)


def _print_workflow(w: Workflow, file=sys.stdout) -> str:
    print("nextflow.enable.dsl = 2", file=file)

    print("", file=file)
    _print_bodies(w, file=file)
    print("", file=file)
    print(f"workflow {{\n\t{w.name}()\n}}", file=file)
