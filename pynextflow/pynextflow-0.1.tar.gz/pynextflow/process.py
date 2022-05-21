from collections.abc import Iterable

import inspect
import os
import pathlib
from typing import List, Callable, Any

import pynextflow
from pynextflow import Local
from pynextflow.entities import InOut, Path, Bash, Variable
from pynextflow.entities.process import Process
from pynextflow.entities.workflow import Workflow
from pynextflow.executors import _get_executor, _executor_started


def _process_decorator(_func=None, *,
                       # Directives
                       tag: str = None,
                       publish_dir: str = None,
                       echo: bool = False,

                       # Input
                       input: List[InOut] = None,

                       # Output
                       output: List[InOut] = None
                       ) -> Callable[[Callable[..., Process]], Callable[..., Process]]:
    def decorator_process(func: Callable[..., Any]) -> Callable[..., Process]:
        def inner(*args, **kwargs) -> Process:
            executor = _get_executor()
            sig = inspect.signature(func)

            # Python native execution of a process
            if not _executor_started() and executor is None:
                if issubclass(sig.return_annotation, Bash):
                    return os.system(func(*args, **kwargs))
                else:
                    return func(*args, **kwargs)

            # Directives
            directives = {}
            if tag:
                directives['tag'] = tag
            if publish_dir:
                directives['publishDir'] = publish_dir
            if echo:
                directives['echo'] = Variable('true')

            # Deduce inputs from signature
            final_inputs = input
            if not final_inputs:
                final_inputs = [_parameter_to_def(param) for name, param in sig.parameters.items()]
                final_inputs = [pynextflow.tuple(*final_inputs)] if len(final_inputs) > 1 else final_inputs

            # Build process
            process = Process(func, args, directives, final_inputs, output)
            if _executor_started():
                return process

            args_body = ""
            # We don't want the local executor to consume the args
            if not isinstance(executor, Local):
                args_body = ",".join([_build_arg(a, p.annotation) for a, p in zip(args, sig.parameters.values())])

            returns = process.is_python()
            wbody = f"workflow pynextflow {{ _return_result({process.name}({args_body}).collect())}}" if returns else f"workflow pynextflow {{ {process.name}({args_body})}}"

            w = Workflow("pynextflow", [process], wbody, args, func)
            return executor.run(w, returns=returns)

        return inner

    if _func is None:
        return decorator_process
    else:
        return decorator_process(_func)


def _build_arg(arg, arg_type, recursive=False):
    if isinstance(arg, str):
        return repr(arg)

    if isinstance(arg, tuple):
        return "[" + ",".join([_build_arg(a, None, recursive=True) for a in arg]) + "]"

    if not recursive and isinstance(arg, Iterable):
        if issubclass(arg_type, Path):
            return "Channel.fromPath([" + ",".join(_build_arg(v, None, recursive=True) for v in arg) + "])"
        return "Channel.of(" + ",".join(_build_arg(v, None, recursive=True) for v in arg) + ")"

    return repr(arg)


def _parameter_to_def(param):
    # TODO path, file ...
    if issubclass(param.annotation, str):
        return pynextflow.val(param.name)

    if issubclass(param.annotation, pathlib.Path):
        return pynextflow.path(param.name)

    if issubclass(param.annotation, Path):
        return pynextflow.path(param.name)

    return pynextflow.val(param.name)

