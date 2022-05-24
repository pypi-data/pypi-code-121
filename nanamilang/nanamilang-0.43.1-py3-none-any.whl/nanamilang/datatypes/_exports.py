"""NanamiLang, Data Type Method Export"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import inspect
import functools

import nanamilang.spec
from .base import Base


def export():
    """
    NanamiLang export() decorator

    Example usage:

    @export()
    def method(<maybe-dt-args>) -> <some nanamilang dt>:
        ...

    This decorator will lint your data type exportable method
    And in case of success, will mark this method as exported
    But in case of a failure, 'AssertionError' will be raised

    Also, exported data type method will be automatically covered by NanamiLang Spec,
    including 'ArityIs' and 'ArgumentsTypeChainVariants' NanamiLang Spec Engine Rules
    """

    def wrapped(_fn):
        @functools.wraps(_fn)
        def function(*args, **kwargs):

            return _fn(*args, **kwargs)

        signature = inspect.signature(_fn)

        _ret = signature.return_annotation

        _ret_valid = issubclass(_ret, (Base,))

        _args = tuple(map(lambda x: x.annotation, signature.parameters.values()))

        _args = () if len(_args) == 1 else _args[1:]  # <- actual args types classes!

        _args_len = len(_args)

        _args_valid = not tuple(filter(lambda x: not issubclass(x, (Base,)),
                                       _args)) if _args else True  # empty args valid

        _base_nanamilang_integrity_spec = [[nanamilang.spec.Spec.ArityIs, _args_len]]

        _type_chain_spec = [nanamilang.spec.Spec.ArgumentsTypeChainVariants, [_args]]

        if _args:
            _base_nanamilang_integrity_spec.append(_type_chain_spec)  # type checking

        assert _args_valid and _ret_valid, (
            'export: either return or argument(s) type(s) are missing, won\'t export'
        )

        function.specs = _base_nanamilang_integrity_spec  # <- to validate() it later
        function.exported = True  # <- and we can later check whether exported or not

        return function

    return wrapped  # <- then, we can later call exported method using dot-expression
