"""
Plugin to fix the type of certain methods on ``Just`` and ``Nothing`` objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import typing as t

from mypy.types import (  # pylint: disable=no-name-in-module
    Type, Instance, LiteralType
)
from mypy.plugin import (  # pylint: disable=no-name-in-module
    Plugin, MethodContext
)
from mypy.checkmember import \
    analyze_member_access  # pylint: disable=no-name-in-module


def attr_callback(ctx: MethodContext, typ: str) -> Type:
    """Callback to determine type for a ``.attr`` call on a ``Maybe``.
    """
    (attr, ), = ctx.arg_types
    attr_maybe_value: t.Optional[Type] = attr
    if isinstance(attr, Instance):
        attr_maybe_value = attr.last_known_value

    if not isinstance(attr_maybe_value, LiteralType):
        ctx.api.fail(
            'The attr to Maybe.attr should be a literal',
            ctx.context,
        )
        return ctx.default_return_type

    attr_value = attr_maybe_value.value

    if not isinstance(attr_value, str):  # pragma: no cover
        return ctx.default_return_type

    assert isinstance(ctx.type, Instance)
    base, = ctx.type.args
    assert isinstance(base, Instance)
    if not base.has_readable_member(attr_value):
        ctx.api.fail(
            'The {} has no attribute named {}'.format(base, attr_value),
            ctx.context,
        )
        return ctx.default_return_type

    checker = ctx.api.expr_checker  # type: ignore

    member = analyze_member_access(
        attr_value,
        base,
        ctx.context,
        is_lvalue=False,
        is_super=False,
        is_operator=True,
        msg=checker.msg,
        original_type=base,
        chk=checker.chk,
        in_literal_context=checker.is_literal_context(),
    )
    return ctx.api.named_generic_type(typ, [member])


class CgMaybePlugin(Plugin):
    """Mypy plugin definition.
    """

    def get_method_hook(  # pylint: disable=no-self-use
        self,
        fullname: str,
    ) -> t.Optional[t.Callable[[MethodContext], Type]]:
        """Get the function to be called by mypy.
        """
        if fullname == 'cg_maybe._just.Just.attr':
            return lambda ctx: attr_callback(ctx, 'cg_maybe.Just')
        elif fullname == 'cg_maybe._nothing._Nothing.attr':
            return lambda ctx: attr_callback(ctx, 'cg_maybe._Nothing')
        return None


def plugin(_: str) -> t.Type[CgMaybePlugin]:
    """Get the mypy plugin definition.
    """
    # ignore version argument if the plugin works with all mypy versions.
    return CgMaybePlugin
