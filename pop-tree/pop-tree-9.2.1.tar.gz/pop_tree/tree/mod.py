import inspect
import textwrap
from collections import OrderedDict
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Tuple

import aiofiles

UNKNOWN_REF = "< unknown ref >"


def get_ref(hub, mod) -> str:
    """
    Try to find a reference on the hub for the given mod
    """
    try:
        sister_func = next(iter(mod._funcs.values()))
        return sister_func.ref
    except StopIteration:
        ...


def serialize_signature(hub, signature: inspect.Signature):
    ret = OrderedDict()
    for p in signature.parameters:
        param: inspect.Parameter = signature.parameters[p]
        ret[param.name] = {}
        if param.default is not inspect._empty:
            ret[param.name]["default"] = param.default
        if param.annotation is not inspect._empty:
            ret[param.name]["annotation"] = str(param.annotation)

    final_ret = {"parameters": ret}
    if signature.return_annotation is not inspect._empty:
        final_ret["return_annotation"] = signature.return_annotation
    return final_ret


def format_func(hub, f: Callable, **kwargs):
    lines, start_line = hub.tree.mod.get_source_lines(f)
    return {
        "doc": textwrap.dedent(str(f.__doc__ or "")).strip("\n"),
        "file": inspect.getfile(f),
        "start_line_number": start_line,
        "end_line_number": start_line + len(lines),
        **kwargs,
    }


def funcs(hub, mod, ref: str) -> List[str] or Dict[str, str]:
    """
    Find all of the loaded functions in a pop plugin. I.E:
        pprint(hub.pop.tree.funcs(hub.pop.tree))
    :param hub: The redistributed pop central hub
    :param mod: A plugin that has been loaded onto a sub
    :param ref: The current reference on the hub
    :return: A Dictionary of loaded modules names mapped to a list of their functions
    """
    funcs = sorted(mod._funcs.keys())
    ret = {}
    for f in funcs:
        contract = mod._funcs[f]
        func_info = hub.tree.mod.format_func(
            contract.func,
            ref=f"{ref}.{f}",
            contracts={
                contract_type: [f"{c.ref}.{c.func.__name__}" for c in contracts]
                for contract_type, contracts in contract.contract_functions.items()
            },
        )
        func_info.update(
            hub.tree.mod.serialize_signature(contract.signature),
        )
        ret[f] = func_info
    return ret


def _format_var(name: str, value: Any, source_lines: List[str], **kwargs):
    line_number = 0
    for num, line in enumerate(source_lines):
        if name in line:
            line_number = num + 1
            break

    return {
        "type": value.__class__.__name__,
        "value": value,
        "start_line_number": line_number,
        **kwargs,
    }


async def data(hub, mod, ref: str) -> List[str] or Dict[str, str]:
    """
    Find all of the loaded data in a pop plugin. I.E:
        pprint(hub.pop.tree.data(hub.pop.tree))
    :param hub: The redistributed pop central hub
    :param mod: A plugin that has been loaded onto a sub
    :param ref: The current reference on the hub
    """
    datas = sorted(x for x in mod._vars if x.isupper() and not x.startswith("_"))
    ret = {}

    source_file = inspect.getsourcefile(mod)
    async with aiofiles.open(source_file, "r") as fh:
        lines = await fh.readlines()

    for d_name in datas:
        ret[d_name] = _format_var(
            d_name, mod._vars[d_name], lines, ref=f"{ref}.{d_name}", file=source_file
        )

    return ret


async def types(hub, mod, ref: str) -> List[str] or Dict[str, str]:
    """
    Find all of the loaded types in a pop plugin. I.E:
        pprint(hub.pop.tree.types(hub.pop.tree))
    :param hub: The redistributed pop central hub
    :param mod: A plugin that has been loaded onto a sub
    :param ref: The current reference on the hub
    """
    classes = sorted(x for x in mod._classes if not x.startswith("_"))
    ret = {}
    for class_name in classes:
        c = mod._classes[class_name]
        source_file = inspect.getsourcefile(c)

        async with aiofiles.open(source_file, "r") as fh:
            source_lines = await fh.readlines()

        try:
            lines, start_line = hub.tree.mod.get_source_lines(c)
        except OSError:
            start_line = 0
            for num, line in enumerate(source_lines):
                if class_name in line:
                    start_line = num + 1
                    break
            lines = []

        signature = inspect.signature(c.__init__)
        functions = {}
        variables = {}
        attributes = []
        for name, value in inspect.getmembers(c):
            if name.startswith("_"):
                continue
            attributes.append(name)
            attr_ref = f"{ref}.{class_name}.{name}"
            if inspect.isfunction(value):
                functions[name] = hub.tree.mod.format_func(value, ref=attr_ref)
            else:
                variables[name] = _format_var(
                    name, value, source_lines, ref=attr_ref, file=source_file
                )
        class_info = {
            "ref": f"{ref}.{class_name}",
            "doc": textwrap.dedent(c.__doc__ or "").strip("\n"),
            "signature": hub.tree.mod.serialize_signature(signature),
            "attributes": attributes,
            "functions": functions,
            "variables": variables,
            "file": source_file,
            "start_line_number": start_line,
            "end_line_number": start_line + len(lines),
        }
        ret[class_name] = class_info
    return ret


async def parse(hub, mod, ref: str) -> Dict[str, Any]:
    """
    Parse a loaded mod object

    :param hub: The redistributed pop central hub
    :param mod: A plugin that has been loaded onto a sub
    :param ref: The current reference on the hub
    """
    return {
        "ref": ref,
        "doc": (mod._attrs.get("__doc__") or "").strip(),
        "file": getattr(mod, "__file__", None),
        "attributes": sorted(
            a for a in mod._attrs if not (a.startswith("__") and a.endswith("__"))
        ),
        "classes": await hub.tree.mod.types(mod, ref),
        "functions": hub.tree.mod.funcs(mod, ref),
        "variables": await hub.tree.mod.data(mod, ref),
    }


def get_source_lines(hub, module: Callable) -> Tuple[List, int]:
    try:
        return inspect.getsourcelines(module)
    except OSError:
        # This can happen when running pop-tree from within a binary
        return [], -1
