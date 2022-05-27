#
# Copyright 2021 Simple Machines Pty Ltd - All Rights Reserved.
#
# This file is part of Anaml.
#
# Unauthorized copying and/or distribution of this file, via any medium is
# strictly prohibited.
#
"""Extend dataclasses with a copy() method a la Scala case classes.

This module defines a @persistent decorator to extend dataclasses (typically
frozen dataclasses) with a copy() method. Like the Scala equivalent, this method
creates and returns a new instance of the dataclass with the same field values.
Also like the Scala equivalent, this method allows the caller to override the
value for one or more fields.

This essentially bolts the `dataclasses.replace` onto each class in such a way
that it has formal parameters that match the fields of the class.

The general approach (and much of the code) was taken from the dataclasses
module in the standard library. As such it is covered by the same license as
dataclasses.py. As far as I can tell this is the PSF License or maybe the
Apache Foundation License (judging by the 3.6 backport on PyPI).
"""

import builtins
import dataclasses
import sys

from typing import Optional, List, Union, Callable, Type


# We use this so we can distinguish between an optional argument that was not given, and
# one that was given with the value None.
class _MissingType:
    def __repr__(self) -> str:
        return 'None'


_MISSING = _MissingType()
_COPY_METHOD_NAME = "copy"
_PERSISTENT_METHOD_MARKER = "__persistent_method__"


def _create_fn(
    name: str,
    args: List[str],
    body: List[str],
    *,
    doc: Optional[str] = None,
    globals: Optional[dict] = None,
    locals: Optional[dict] = None,
    return_type: Union[_MissingType, type] = _MISSING
) -> Callable:
    # This is stolen from dataclasses with the addition of doc.

    # Note that we mutate locals when exec() is called.  Caller
    # beware!  The only callers are internal to this module, so no
    # worries about external callers.
    if locals is None:
        locals = {}
    if 'BUILTINS' not in locals:
        locals['BUILTINS'] = builtins
    return_annotation = ''
    if return_type is not _MISSING:
        locals['_return_type'] = return_type
        return_annotation = '->_return_type'
    args = ','.join(args)
    body = '\n'.join(f'  {b}' for b in body)

    # Compute the text of the entire function.
    txt = f' def {name}({args}){return_annotation}:\n{body}'

    local_vars = ', '.join(locals.keys())
    txt = f"def __create_fn__({local_vars}):\n{txt}\n return {name}"

    ns = {}
    exec(txt, globals, ns)
    f = ns['__create_fn__'](**locals)

    # We use this to mark all methods we generate. This lets us replace them when processing subclasses without
    # accidentally also replacing methods defined by the client.
    setattr(f, _PERSISTENT_METHOD_MARKER, True)

    if doc is not None:
        f.__doc__ = doc

    return f


def _make_copy_fn(cls: type, method_name: str, self_name: str, globals: dict) -> Callable:
    # Build a copy() method. This method accepts keyword parameters for every
    # dataclass field declared with field.init=True. It creates and returns a
    # new instance with the existing values together with each of the keyword
    # arguments actually given.
    locals = {
        'MISSING': _MISSING,
        'Optional': Optional,
        '__my_klass__': cls,
    }
    parameters = [self_name, '*']
    body_lines = ['values = {}']

    for f in dataclasses.fields(cls):
        if f.init:
            # Add the field type to the locals so that it's available when the
            # parameter definition is evaluated.
            locals[f'_type_{f.name}'] = f.type
            # Add the parameter definition to the function code.
            parameters.append(
                f'{f.name}: Optional[_type_{f.name}] = MISSING'
            )
            # Add code to copy or override the fields.
            body_lines += [
                f'if {f.name} is MISSING:',
                f'  values["{f.name}"] = getattr(self, "{f.name}")',
                'else:',
                f'  values["{f.name}"] = {f.name}',
            ]

    # Finally, return a new instance with the values we copied.
    body_lines.append(
        'return __my_klass__(**values)'
    )

    doc = "Return a copy of this object with the specified fields overridden."

    return _create_fn(
        method_name,
        parameters,
        body_lines,
        doc=doc,
        locals=locals,
        globals=globals,
        return_type=cls,
    )


def _process_persistent(cls: Type) -> Type:
    if not dataclasses.is_dataclass(cls):
        raise TypeError(f"{cls.__name__} is not a dataclass; only data classes can be made persistent")

    # We don't want to silently obliterate methods defined by the user, but we
    # also don't want to bother with a configurable method name. Just reject
    # classes that already define a copy attribute.
    if hasattr(cls, _COPY_METHOD_NAME) and not hasattr(getattr(cls, _COPY_METHOD_NAME), _PERSISTENT_METHOD_MARKER):
        raise TypeError(
            f"Cannot make {cls.__name__} persistent: it already has a method or field called '{_COPY_METHOD_NAME}'"
        )

    class_globals = sys.modules[cls.__module__].__dict__
    self_name = "self" if "self" not in dataclasses.fields(cls) else "__persistent_self__"

    setattr(cls, _COPY_METHOD_NAME, _make_copy_fn(cls, _COPY_METHOD_NAME, self_name, class_globals))

    return cls


def persistent(cls: Optional[Type] = None) -> Union[Callable[[Type], Type], Type]:
    """Enhance dataclasses with a copy() helper method."""

    def wrap(cls: Type) -> Type:
        return _process_persistent(cls)

    if cls is None:
        return wrap

    return wrap(cls)
