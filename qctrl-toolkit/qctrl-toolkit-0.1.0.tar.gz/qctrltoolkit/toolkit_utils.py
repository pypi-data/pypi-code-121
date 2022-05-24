# Copyright 2022 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""
Utility functions for exposing and binding toolkits.
"""
import inspect
from functools import partial
from typing import (
    Any,
    Callable,
    List,
    Optional,
    Union,
)

import forge
from numpydoc.docscrape import NumpyDocString
from qctrlcommons.exceptions import QctrlException

from qctrltoolkit.namespace import Namespace

# parameters like qctrl/graph in the toolkit functions are just placeholder for the actual object
# need to remove them from the doc/signature before binding in python
_EXCLUDE_PARAMETERS = {"qctrl", "graph"}

TOOLKIT_ATTR = "_toolkit_attr"


def expose(namespaces: Union[Namespace, List[Namespace]]):
    """
    Define a decorator, which inserts a label of the namespaces for later binding to the
    wrapped object.

    The decorator sets a new attribute defined by TOOLKIT_ATTR to the object, which is a tuple
    of strings defining the namespaces. You can apply this decorator to the toolkit function/class,
    and they will be bound to the corresponding namespaces when initializing the Qctrl/Graph object.

    For example, to expose a function to one namespace ::

        @expose(Namespace.SUPERCONDUCTING)
        def some_func()

    To expose a function to multiple namespaces, as it maybe be reused for
    different physical systems ::

        @expose([Namespace.SUPERCONDUCTING, Namespace.IONS])
        def some_general_func()
    """
    if not isinstance(namespaces, list):
        namespaces = [namespaces]
    return partial(_expose, attr=tuple(namespaces))


def _expose(obj, attr):
    setattr(obj, TOOLKIT_ATTR, attr)
    return obj


def forge_toolkit(toolkit: Any, obj: Any) -> Any:
    """
    Forge the toolkit object (must be a function or class) for binding.

    Note that when toolkit is a class, we just return is, since it should
    not accept the to-be-bound object, to avoid the cyclic access.

    Parameters
    ----------
    toolkit : Any
        A toolkit function to be forged.
    obj: Any
        The object to which the forged toolkit is bound.

    Returns
    -------
    Any
        A forged class/function.

    Raises
    ------
    QctrlException
        If toolkit has an unsupported type.
    """

    if inspect.isfunction(toolkit):
        return _forge_func(toolkit, obj)
    if inspect.isclass(toolkit):
        return toolkit
    raise QctrlException(
        f"Toolkit must either be a function or a class, but got {type(toolkit)}."
    )


def _forge_func(func: Callable, obj: Any) -> Callable:
    """
    Forge toolkit function.
    """

    def forged(*arg, **kwargs):
        return func(obj, *arg, **kwargs)

    _args, _kwargs, _return_type, bind_obj = _get_args_kwargs_return_type(func)

    if not bind_obj:
        return func

    assert func.__doc__ is not None, f"{func} has no doc."
    forged.__doc__ = _clean_doc(func.__doc__)
    forged.__name__ = func.__name__
    sig = forge.sign(*_args, **_kwargs)
    forged = sig(forged)
    forged = forge.returns(_return_type)(forged)

    return forged


def _get_args_kwargs_return_type(func):
    """
    Get the information about the function signature.

    Returns a tuple, where the first element is list of args,
    the second is dictionary for kwargs,
    and the last one the type of the returned value.
    This will be used to forge a new function for binding.
    """
    _args = []
    _kwargs = {}
    bind_obj = False
    _func_inspected = inspect.signature(func)
    for arg_name, _arg in _func_inspected.parameters.items():
        # note that some convenience function might not be fetchable
        if arg_name == "name":
            _kwargs = {"name": forge.kwarg("name", type=Optional[str], default=None)}
        elif arg_name in _EXCLUDE_PARAMETERS:
            bind_obj = True
        else:
            _args.append(
                forge.arg(arg_name, type=_arg.annotation, default=_arg.default)
            )

    return _args, _kwargs, _func_inspected.return_annotation, bind_obj


def _clean_doc(doc: str) -> str:
    """
    Removes unnecessary part from the doc.
    """
    doc_obj = NumpyDocString(doc)

    doc_obj["Parameters"] = [
        item for item in doc_obj["Parameters"] if item.name not in _EXCLUDE_PARAMETERS
    ]

    return doc_obj.__str__()
