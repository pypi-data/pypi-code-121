"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations
import inspect

from typing import (
    Any,
    Callable,
    ClassVar,
    Coroutine,
    Dict,
    Generator,
    Generic,
    List,
    MutableMapping,
    Optional,
    Set,
    TYPE_CHECKING,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)
from textwrap import TextWrapper

import re

from ..enums import AppCommandOptionType, AppCommandType
from .models import Choice
from .transformers import annotation_to_parameter, CommandParameter, NoneType
from .errors import AppCommandError, CheckFailure, CommandInvokeError, CommandSignatureMismatch, CommandAlreadyRegistered
from ..message import Message
from ..user import User
from ..member import Member
from ..permissions import Permissions
from ..utils import resolve_annotation, MISSING, is_inside_class, maybe_coroutine, async_all

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, Concatenate
    from ..interactions import Interaction
    from ..abc import Snowflake
    from .namespace import Namespace
    from .models import ChoiceT

    # Generally, these two libraries are supposed to be separate from each other.
    # However, for type hinting purposes it's unfortunately necessary for one to
    # reference the other to prevent type checking errors in callbacks
    from discord.ext.commands import Cog

    ErrorFunc = Callable[[Interaction, AppCommandError], Coroutine[Any, Any, None]]

__all__ = (
    'Command',
    'ContextMenu',
    'Group',
    'context_menu',
    'command',
    'describe',
    'check',
    'rename',
    'choices',
    'autocomplete',
    'guilds',
    'guild_only',
    'default_permissions',
)

if TYPE_CHECKING:
    P = ParamSpec('P')
else:
    P = TypeVar('P')

T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])
GroupT = TypeVar('GroupT', bound='Binding')
Coro = Coroutine[Any, Any, T]
UnboundError = Callable[['Interaction', AppCommandError], Coro[Any]]
Error = Union[
    Callable[[GroupT, 'Interaction', AppCommandError], Coro[Any]],
    UnboundError,
]
Check = Callable[['Interaction'], Union[bool, Coro[bool]]]
Binding = Union['Group', 'Cog']


if TYPE_CHECKING:
    CommandCallback = Union[
        Callable[Concatenate[GroupT, 'Interaction', P], Coro[T]],
        Callable[Concatenate['Interaction', P], Coro[T]],
    ]

    ContextMenuCallback = Union[
        # If groups end up support context menus these would be uncommented
        # Callable[[GroupT, 'Interaction', Member], Coro[Any]],
        # Callable[[GroupT, 'Interaction', User], Coro[Any]],
        # Callable[[GroupT, 'Interaction', Message], Coro[Any]],
        # Callable[[GroupT, 'Interaction', Union[Member, User]], Coro[Any]],
        Callable[['Interaction', Member], Coro[Any]],
        Callable[['Interaction', User], Coro[Any]],
        Callable[['Interaction', Message], Coro[Any]],
        Callable[['Interaction', Union[Member, User]], Coro[Any]],
    ]

    AutocompleteCallback = Union[
        Callable[[GroupT, 'Interaction', ChoiceT], Coro[List[Choice[ChoiceT]]]],
        Callable[['Interaction', ChoiceT], Coro[List[Choice[ChoiceT]]]],
    ]
else:
    CommandCallback = Callable[..., Coro[T]]
    ContextMenuCallback = Callable[..., Coro[T]]
    AutocompleteCallback = Callable[..., Coro[T]]


CheckInputParameter = Union['Command[Any, ..., Any]', 'ContextMenu', CommandCallback, ContextMenuCallback]

# The re module doesn't support \p{} so we have to list characters from Thai and Devanagari manually.
THAI_COMBINING = r'\u0e31-\u0e3a\u0e47-\u0e4e'
DEVANAGARI_COMBINING = r'\u0900-\u0903\u093a\u093b\u093c\u093e\u093f\u0940-\u094f\u0955\u0956\u0957\u0962\u0963'
VALID_SLASH_COMMAND_NAME = re.compile(r'^[-_\w' + THAI_COMBINING + DEVANAGARI_COMBINING + r']{1,32}$')

CAMEL_CASE_REGEX = re.compile(r'(?<!^)(?=[A-Z])')

ARG_NAME_SUBREGEX = r'(?:\\?\*){0,2}(?P<name>\w+)'

ARG_DESCRIPTION_SUBREGEX = r'(?P<description>(?:.|\n)+?(?:\Z|\r?\n(?=[\S\r\n])))'

ARG_TYPE_SUBREGEX = r'(?:.+)'

GOOGLE_DOCSTRING_ARG_REGEX = re.compile(
    rf'^{ARG_NAME_SUBREGEX}[ \t]*(?:\({ARG_TYPE_SUBREGEX}\))?[ \t]*:[ \t]*{ARG_DESCRIPTION_SUBREGEX}',
    re.MULTILINE,
)

SPHINX_DOCSTRING_ARG_REGEX = re.compile(
    rf'^:param {ARG_NAME_SUBREGEX}:[ \t]+{ARG_DESCRIPTION_SUBREGEX}',
    re.MULTILINE,
)

NUMPY_DOCSTRING_ARG_REGEX = re.compile(
    rf'^{ARG_NAME_SUBREGEX}(?:[ \t]*:)?(?:[ \t]+{ARG_TYPE_SUBREGEX})?[ \t]*\r?\n[ \t]+{ARG_DESCRIPTION_SUBREGEX}',
    re.MULTILINE,
)


def _shorten(
    input: str,
    *,
    _wrapper: TextWrapper = TextWrapper(width=100, max_lines=1, replace_whitespace=True, placeholder='…'),
) -> str:
    try:
        # split on the first double newline since arguments may appear after that
        input, _ = re.split(r'\n\s*\n', input, maxsplit=1)
    except ValueError:
        pass
    return _wrapper.fill(' '.join(input.strip().split()))


def _parse_args_from_docstring(func: Callable[..., Any], params: Dict[str, CommandParameter]) -> Dict[str, str]:
    docstring = inspect.getdoc(func)

    if docstring is None:
        return {}

    # Extract the arguments
    # Note: These are loose regexes, but they are good enough for our purposes
    # For Google-style, look only at the lines that are indented
    section_lines = inspect.cleandoc('\n'.join(line for line in docstring.splitlines() if line.startswith('  ')))
    docstring_styles = (
        GOOGLE_DOCSTRING_ARG_REGEX.finditer(section_lines),
        SPHINX_DOCSTRING_ARG_REGEX.finditer(docstring),
        NUMPY_DOCSTRING_ARG_REGEX.finditer(docstring),
    )

    return {
        m.group('name'): m.group('description') for matches in docstring_styles for m in matches if m.group('name') in params
    }


def _to_kebab_case(text: str) -> str:
    return CAMEL_CASE_REGEX.sub('-', text).lower()


def validate_name(name: str) -> str:
    match = VALID_SLASH_COMMAND_NAME.match(name)
    if match is None:
        raise ValueError(
            f'{name!r} must be between 1-32 characters and contain only lower-case letters, numbers, hyphens, or underscores.'
        )

    # Ideally, name.islower() would work instead but since certain characters
    # are Lo (e.g. CJK) those don't pass the test. I'd use `casefold` instead as
    # well, but chances are the server-side check is probably something similar to
    # this code anyway.
    if name.lower() != name:
        raise ValueError(f'{name!r} must be all lower-case')
    return name


def validate_context_menu_name(name: str) -> str:
    if not name or len(name) > 32:
        raise ValueError('context menu names must be between 1-32 characters')
    return name


def _validate_auto_complete_callback(
    callback: AutocompleteCallback[GroupT, ChoiceT],
    skip_binding: bool = False,
) -> AutocompleteCallback[GroupT, ChoiceT]:

    binding = getattr(callback, '__self__', None)
    if binding is not None:
        callback = callback.__func__
        requires_binding = True
    else:
        requires_binding = is_inside_class(callback) or skip_binding

    callback.requires_binding = requires_binding
    callback.binding = binding

    required_parameters = 2 + requires_binding
    params = inspect.signature(callback).parameters
    if len(params) != required_parameters:
        raise TypeError(f'autocomplete callback {callback.__qualname__!r} requires either 2 or 3 parameters to be passed')

    return callback


def _context_menu_annotation(annotation: Any, *, _none: type = NoneType) -> AppCommandType:
    if annotation is Message:
        return AppCommandType.message

    supported_types: Set[Any] = {Member, User}
    if annotation in supported_types:
        return AppCommandType.user

    # Check if there's an origin
    origin = getattr(annotation, '__origin__', None)
    if origin is not Union:
        # Only Union is supported so bail early
        msg = (
            f'unsupported type annotation {annotation!r}, must be either discord.Member, '
            'discord.User, discord.Message, or a typing.Union of discord.Member and discord.User'
        )
        raise TypeError(msg)

    # Only Union[Member, User] is supported
    if not all(arg in supported_types for arg in annotation.__args__):
        raise TypeError(f'unsupported types given inside {annotation!r}')

    return AppCommandType.user


def _populate_descriptions(params: Dict[str, CommandParameter], descriptions: Dict[str, Any]) -> None:
    for name, param in params.items():
        description = descriptions.pop(name, MISSING)
        if description is MISSING:
            param.description = '…'
            continue

        if not isinstance(description, str):
            raise TypeError('description must be a string')

        param.description = _shorten(description)

    if descriptions:
        first = next(iter(descriptions))
        raise TypeError(f'unknown parameter given: {first}')


def _populate_renames(params: Dict[str, CommandParameter], renames: Dict[str, str]) -> None:
    rename_map: Dict[str, str] = {}

    # original name to renamed name

    for name in params.keys():
        new_name = renames.pop(name, MISSING)

        if new_name is MISSING:
            rename_map[name] = name
            continue

        if name in rename_map:
            raise ValueError(f'{new_name} is already used')

        new_name = validate_name(new_name)
        rename_map[name] = new_name
        params[name]._rename = new_name

    if renames:
        first = next(iter(renames))
        raise ValueError(f'unknown parameter given: {first}')


def _populate_choices(params: Dict[str, CommandParameter], all_choices: Dict[str, List[Choice]]) -> None:
    for name, param in params.items():
        choices = all_choices.pop(name, MISSING)
        if choices is MISSING:
            continue

        if not isinstance(choices, list):
            raise TypeError('choices must be a list of Choice')

        if not all(isinstance(choice, Choice) for choice in choices):
            raise TypeError('choices must be a list of Choice')

        if param.type not in (AppCommandOptionType.string, AppCommandOptionType.number, AppCommandOptionType.integer):
            raise TypeError('choices are only supported for integer, string, or number option types')

        if not all(param.type == choice._option_type for choice in choices):
            raise TypeError('choices must all have the same inner option type as the parameter choice type')

        param.choices = choices

    if all_choices:
        first = next(iter(all_choices))
        raise TypeError(f'unknown parameter given: {first}')


def _populate_autocomplete(params: Dict[str, CommandParameter], autocomplete: Dict[str, Any]) -> None:
    for name, param in params.items():
        callback = autocomplete.pop(name, MISSING)
        if callback is MISSING:
            continue

        if not inspect.iscoroutinefunction(callback):
            raise TypeError('autocomplete callback must be a coroutine function')

        if param.type not in (AppCommandOptionType.string, AppCommandOptionType.number, AppCommandOptionType.integer):
            raise TypeError('autocomplete is only supported for integer, string, or number option types')

        if param.is_choice_annotation():
            raise TypeError(
                'Choice annotation unsupported for autocomplete parameters, consider using a regular annotation instead'
            )

        param.autocomplete = _validate_auto_complete_callback(callback)

    if autocomplete:
        first = next(iter(autocomplete))
        raise TypeError(f'unknown parameter given: {first}')


def _extract_parameters_from_callback(func: Callable[..., Any], globalns: Dict[str, Any]) -> Dict[str, CommandParameter]:
    params = inspect.signature(func).parameters
    cache = {}
    required_params = is_inside_class(func) + 1
    if len(params) < required_params:
        raise TypeError(f'callback {func.__qualname__!r} must have more than {required_params - 1} parameter(s)')

    iterator = iter(params.values())
    for _ in range(0, required_params):
        next(iterator)

    parameters: List[CommandParameter] = []
    for parameter in iterator:
        if parameter.annotation is parameter.empty:
            raise TypeError(f'parameter {parameter.name!r} is missing a type annotation in callback {func.__qualname__!r}')

        resolved = resolve_annotation(parameter.annotation, globalns, globalns, cache)
        param = annotation_to_parameter(resolved, parameter)
        parameters.append(param)

    values = sorted(parameters, key=lambda a: a.required, reverse=True)
    result = {v.name: v for v in values}

    descriptions = _parse_args_from_docstring(func, result)

    try:
        descriptions.update(func.__discord_app_commands_param_description__)
    except AttributeError:
        for param in values:
            if param.description is MISSING:
                param.description = '…'
    if descriptions:
        _populate_descriptions(result, descriptions)

    try:
        renames = func.__discord_app_commands_param_rename__
    except AttributeError:
        pass
    else:
        _populate_renames(result, renames.copy())

    try:
        choices = func.__discord_app_commands_param_choices__
    except AttributeError:
        pass
    else:
        _populate_choices(result, choices.copy())

    try:
        autocomplete = func.__discord_app_commands_param_autocomplete__
    except AttributeError:
        pass
    else:
        _populate_autocomplete(result, autocomplete.copy())

    return result


def _get_context_menu_parameter(func: ContextMenuCallback) -> Tuple[str, Any, AppCommandType]:
    params = inspect.signature(func).parameters
    if len(params) != 2:
        msg = (
            f'context menu callback {func.__qualname__!r} requires 2 parameters, '
            'the first one being the interaction and the other one explicitly '
            'annotated with either discord.Message, discord.User, discord.Member, '
            'or a typing.Union of discord.Member and discord.User'
        )
        raise TypeError(msg)

    iterator = iter(params.values())
    next(iterator)  # skip interaction
    parameter = next(iterator)
    if parameter.annotation is parameter.empty:
        msg = (
            f'second parameter of context menu callback {func.__qualname__!r} must be explicitly '
            'annotated with either discord.Message, discord.User, discord.Member, or '
            'a typing.Union of discord.Member and discord.User'
        )
        raise TypeError(msg)

    resolved = resolve_annotation(parameter.annotation, func.__globals__, func.__globals__, {})
    type = _context_menu_annotation(resolved)
    return (parameter.name, resolved, type)


class Command(Generic[GroupT, P, T]):
    """A class that implements an application command.

    These are usually not created manually, instead they are created using
    one of the following decorators:

    - :func:`~discord.app_commands.command`
    - :meth:`Group.command <discord.app_commands.Group.command>`
    - :meth:`CommandTree.command <discord.app_commands.CommandTree.command>`

    .. versionadded:: 2.0

    Attributes
    ------------
    name: :class:`str`
        The name of the application command.
    description: :class:`str`
        The description of the application command. This shows up in the UI to describe
        the application command.
    checks
        A list of predicates that take a :class:`~discord.Interaction` parameter
        to indicate whether the command callback should be executed. If an exception
        is necessary to be thrown to signal failure, then one inherited from
        :exc:`AppCommandError` should be used. If all the checks fail without
        propagating an exception, :exc:`CheckFailure` is raised.
    default_permissions: Optional[:class:`~discord.Permissions`]
        The default permissions that can execute this command on Discord. Note
        that server administrators can override this value in the client.
        Setting an empty permissions field will disallow anyone except server
        administrators from using the command in a guild.

        Due to a Discord limitation, this does not work on subcommands.
    guild_only: :class:`bool`
        Whether the command should only be usable in guild contexts.
        Defaults to ``False``.

        Due to a Discord limitation, this does not work on subcommands.
    parent: Optional[:class:`Group`]
        The parent application command. ``None`` if there isn't one.
    """

    def __init__(
        self,
        *,
        name: str,
        description: str,
        callback: CommandCallback[GroupT, P, T],
        parent: Optional[Group] = None,
        guild_ids: Optional[List[int]] = None,
    ):
        self.name: str = validate_name(name)
        self.description: str = description
        self._attr: Optional[str] = None
        self._callback: CommandCallback[GroupT, P, T] = callback
        self.parent: Optional[Group] = parent
        self.binding: Optional[GroupT] = None
        self.on_error: Optional[Error[GroupT]] = None
        self.module: Optional[str] = callback.__module__

        # Unwrap __self__ for bound methods
        try:
            self.binding = callback.__self__
            self._callback = callback = callback.__func__
        except AttributeError:
            pass

        self._params: Dict[str, CommandParameter] = _extract_parameters_from_callback(callback, callback.__globals__)
        self.checks: List[Check] = getattr(callback, '__discord_app_commands_checks__', [])
        self._guild_ids: Optional[List[int]] = guild_ids or getattr(
            callback, '__discord_app_commands_default_guilds__', None
        )
        self.default_permissions: Optional[Permissions] = getattr(
            callback, '__discord_app_commands_default_permissions__', None
        )
        self.guild_only: bool = getattr(callback, '__discord_app_commands_guild_only__', False)

        if self._guild_ids is not None and self.parent is not None:
            raise ValueError('child commands cannot have default guilds set, consider setting them in the parent instead')

    def __set_name__(self, owner: Type[Any], name: str) -> None:
        self._attr = name

    @property
    def callback(self) -> CommandCallback[GroupT, P, T]:
        """:ref:`coroutine <coroutine>`: The coroutine that is executed when the command is called."""
        return self._callback

    def _copy_with(
        self,
        *,
        parent: Optional[Group],
        binding: GroupT,
        bindings: MutableMapping[GroupT, GroupT] = MISSING,
        set_on_binding: bool = True,
    ) -> Command:
        bindings = {} if bindings is MISSING else bindings

        cls = self.__class__
        copy = cls.__new__(cls)
        copy.name = self.name
        copy._guild_ids = self._guild_ids
        copy.checks = self.checks
        copy.description = self.description
        copy.default_permissions = self.default_permissions
        copy.guild_only = self.guild_only
        copy._attr = self._attr
        copy._callback = self._callback
        copy.on_error = self.on_error
        copy._params = self._params.copy()
        copy.module = self.module
        copy.parent = parent
        copy.binding = bindings.get(self.binding) if self.binding is not None else binding

        if copy._attr and set_on_binding:
            setattr(copy.binding, copy._attr, copy)

        return copy

    def to_dict(self) -> Dict[str, Any]:
        # If we have a parent then our type is a subcommand
        # Otherwise, the type falls back to the specific command type (e.g. slash command or context menu)
        option_type = AppCommandType.chat_input.value if self.parent is None else AppCommandOptionType.subcommand.value
        base: Dict[str, Any] = {
            'name': self.name,
            'description': self.description,
            'type': option_type,
            'options': [param.to_dict() for param in self._params.values()],
        }

        if self.parent is None:
            base['dm_permission'] = not self.guild_only
            base['default_member_permissions'] = self.default_permissions and self.default_permissions.value

        return base

    async def _invoke_error_handler(self, interaction: Interaction, error: AppCommandError) -> None:
        # These type ignores are because the type checker can't narrow this type properly.
        if self.on_error is not None:
            if self.binding is not None:
                await self.on_error(self.binding, interaction, error)  # type: ignore
            else:
                await self.on_error(interaction, error)  # type: ignore

        parent = self.parent
        if parent is not None:
            await parent.on_error(interaction, error)

            if parent.parent is not None:
                await parent.parent.on_error(interaction, error)

    def _has_any_error_handlers(self) -> bool:
        if self.on_error is not None:
            return True

        parent = self.parent
        if parent is not None:
            # Check if the on_error is overridden
            if parent.__class__.on_error is not Group.on_error:
                return True

            if parent.parent is not None:
                parent_cls = parent.parent.__class__
                if parent_cls.on_error is not Group.on_error:
                    return True

        return False

    async def _transform_arguments(self, interaction: Interaction, namespace: Namespace) -> Dict[str, Any]:
        values = namespace.__dict__
        transformed_values = {}

        for param in self._params.values():
            try:
                value = values[param.display_name]
            except KeyError:
                if not param.required:
                    transformed_values[param.name] = param.default
                else:
                    raise CommandSignatureMismatch(self) from None
            else:
                transformed_values[param.name] = await param.transform(interaction, value)

        return transformed_values

    async def _do_call(self, interaction: Interaction, params: Dict[str, Any]) -> T:
        # These type ignores are because the type checker doesn't quite understand the narrowing here
        # Likewise, it thinks we're missing positional arguments when there aren't any.
        try:
            if self.binding is not None:
                return await self._callback(self.binding, interaction, **params)  # type: ignore
            return await self._callback(interaction, **params)  # type: ignore
        except TypeError as e:
            # In order to detect mismatch from the provided signature and the Discord data,
            # there are many ways it can go wrong yet all of them eventually lead to a TypeError
            # from the Python compiler showcasing that the signature is incorrect. This lovely
            # piece of code essentially checks the last frame of the caller and checks if the
            # locals contains our `self` reference.
            #
            # This is because there is a possibility that a TypeError is raised within the body
            # of the function, and in that case the locals wouldn't contain a reference to
            # the command object under the name `self`.
            frame = inspect.trace()[-1].frame
            if frame.f_locals.get('self') is self:
                raise CommandSignatureMismatch(self) from None
            raise CommandInvokeError(self, e) from e
        except AppCommandError:
            raise
        except Exception as e:
            raise CommandInvokeError(self, e) from e

    async def _invoke_with_namespace(self, interaction: Interaction, namespace: Namespace) -> T:
        if not await self._check_can_run(interaction):
            raise CheckFailure(f'The check functions for command {self.name!r} failed.')

        transformed_values = await self._transform_arguments(interaction, namespace)
        return await self._do_call(interaction, transformed_values)

    async def _invoke_autocomplete(self, interaction: Interaction, name: str, namespace: Namespace):
        # The namespace contains the Discord provided names so this will be fine
        # even if the name is renamed
        value = namespace.__dict__[name]

        try:
            param = self._params[name]
        except KeyError:
            # Slow case, it might be a rename
            params = {param.display_name: param for param in self._params.values()}
            try:
                param = params[name]
            except KeyError:
                raise CommandSignatureMismatch(self) from None

        if param.autocomplete is None:
            raise CommandSignatureMismatch(self)

        predicates = getattr(param.autocomplete, '__discord_app_commands_checks__', [])
        if predicates:
            try:
                if not await async_all(f(interaction) for f in predicates):
                    if not interaction.response.is_done():
                        await interaction.response.autocomplete([])
                    return
            except Exception:
                if not interaction.response.is_done():
                    await interaction.response.autocomplete([])
                return

        if param.autocomplete.requires_binding:
            binding = param.autocomplete.binding or self.binding
            if binding is not None:
                choices = await param.autocomplete(binding, interaction, value)
            else:
                raise TypeError('autocomplete parameter expected a bound self parameter but one was not provided')
        else:
            choices = await param.autocomplete(interaction, value)

        if interaction.response.is_done():
            return

        await interaction.response.autocomplete(choices)

    def _get_internal_command(self, name: str) -> Optional[Union[Command, Group]]:
        return None

    @property
    def root_parent(self) -> Optional[Group]:
        """Optional[:class:`Group`]: The root parent of this command."""
        if self.parent is None:
            return None
        parent = self.parent
        return parent.parent or parent

    @property
    def qualified_name(self) -> str:
        """:class:`str`: Returns the fully qualified command name.

        The qualified name includes the parent name as well. For example,
        in a command like ``/foo bar`` the qualified name is ``foo bar``.
        """
        # A B C
        #     ^ self
        #   ^ parent
        # ^ grandparent
        if self.parent is None:
            return self.name

        names = [self.name, self.parent.name]
        grandparent = self.parent.parent
        if grandparent is not None:
            names.append(grandparent.name)

        return ' '.join(reversed(names))

    async def _check_can_run(self, interaction: Interaction) -> bool:
        if self.parent is not None and self.parent is not self.binding:
            # For commands with a parent which isn't the binding, i.e.
            # <binding>
            #     <parent>
            #         <command>
            # The parent check needs to be called first
            if not await maybe_coroutine(self.parent.interaction_check, interaction):
                return False

        if self.binding is not None:
            check: Optional[Check] = getattr(self.binding, 'interaction_check', None)
            if check:
                ret = await maybe_coroutine(check, interaction)
                if not ret:
                    return False

        predicates = self.checks
        if not predicates:
            return True

        # Type checker does not understand negative narrowing cases like this function
        return await async_all(f(interaction) for f in predicates)  # type: ignore

    def error(self, coro: Error[GroupT]) -> Error[GroupT]:
        """A decorator that registers a coroutine as a local error handler.

        The local error handler is called whenever an exception is raised in the body
        of the command or during handling of the command. The error handler must take
        2 parameters, the interaction and the error.

        The error passed will be derived from :exc:`AppCommandError`.

        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the local error handler.

        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """

        if not inspect.iscoroutinefunction(coro):
            raise TypeError('The error handler must be a coroutine.')

        self.on_error = coro
        return coro

    def autocomplete(
        self, name: str
    ) -> Callable[[AutocompleteCallback[GroupT, ChoiceT]], AutocompleteCallback[GroupT, ChoiceT]]:
        """A decorator that registers a coroutine as an autocomplete prompt for a parameter.

        The coroutine callback must have 2 parameters, the :class:`~discord.Interaction`,
        and the current value by the user (usually either a :class:`str`, :class:`int`, or :class:`float`,
        depending on the type of the parameter being marked as autocomplete).

        To get the values from other parameters that may be filled in, accessing
        :attr:`.Interaction.namespace` will give a :class:`Namespace` object with those
        values.

        Parent :func:`checks <check>` are ignored within an autocomplete. However, checks can be added
        to the autocomplete callback and the ones added will be called. If the checks fail for any reason
        then an empty list is sent as the interaction response.

        The coroutine decorator **must** return a list of :class:`~discord.app_commands.Choice` objects.
        Only up to 25 objects are supported.

        Example:

        .. code-block:: python3

            @app_commands.command()
            async def fruits(interaction: discord.Interaction, fruit: str):
                await interaction.response.send_message(f'Your favourite fruit seems to be {fruit}')

            @fruits.autocomplete('fruit')
            async def fruits_autocomplete(
                interaction: discord.Interaction,
                current: str,
            ) -> List[app_commands.Choice[str]]:
                fruits = ['Banana', 'Pineapple', 'Apple', 'Watermelon', 'Melon', 'Cherry']
                return [
                    app_commands.Choice(name=fruit, value=fruit)
                    for fruit in fruits if current.lower() in fruit.lower()
                ]


        Parameters
        -----------
        name: :class:`str`
            The parameter name to register as autocomplete.

        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine or
            the parameter is not found or of an invalid type.
        """

        def decorator(coro: AutocompleteCallback[GroupT, ChoiceT]) -> AutocompleteCallback[GroupT, ChoiceT]:
            if not inspect.iscoroutinefunction(coro):
                raise TypeError('The error handler must be a coroutine.')

            try:
                param = self._params[name]
            except KeyError:
                raise TypeError(f'unknown parameter: {name!r}') from None

            if param.type not in (AppCommandOptionType.string, AppCommandOptionType.number, AppCommandOptionType.integer):
                raise TypeError('autocomplete is only supported for integer, string, or number option types')

            if param.is_choice_annotation():
                raise TypeError(
                    'Choice annotation unsupported for autocomplete parameters, consider using a regular annotation instead'
                )

            param.autocomplete = _validate_auto_complete_callback(coro)
            return coro

        return decorator

    def add_check(self, func: Check, /) -> None:
        """Adds a check to the command.

        This is the non-decorator interface to :func:`check`.

        Parameters
        -----------
        func
            The function that will be used as a check.
        """

        self.checks.append(func)

    def remove_check(self, func: Check, /) -> None:
        """Removes a check from the command.

        This function is idempotent and will not raise an exception
        if the function is not in the command's checks.

        Parameters
        -----------
        func
            The function to remove from the checks.
        """

        try:
            self.checks.remove(func)
        except ValueError:
            pass


class ContextMenu:
    """A class that implements a context menu application command.

    These are usually not created manually, instead they are created using
    one of the following decorators:

    - :func:`~discord.app_commands.context_menu`
    - :meth:`CommandTree.command <discord.app_commands.CommandTree.context_menu>`

    .. versionadded:: 2.0

    Attributes
    ------------
    name: :class:`str`
        The name of the context menu.
    type: :class:`.AppCommandType`
        The type of context menu application command. By default, this is inferred
        by the parameter of the callback.
    default_permissions: Optional[:class:`~discord.Permissions`]
        The default permissions that can execute this command on Discord. Note
        that server administrators can override this value in the client.
        Setting an empty permissions field will disallow anyone except server
        administrators from using the command in a guild.
    guild_only: :class:`bool`
        Whether the command should only be usable in guild contexts.
        Defaults to ``False``.
    checks
        A list of predicates that take a :class:`~discord.Interaction` parameter
        to indicate whether the command callback should be executed. If an exception
        is necessary to be thrown to signal failure, then one inherited from
        :exc:`AppCommandError` should be used. If all the checks fail without
        propagating an exception, :exc:`CheckFailure` is raised.
    """

    def __init__(
        self,
        *,
        name: str,
        callback: ContextMenuCallback,
        type: AppCommandType = MISSING,
        guild_ids: Optional[List[int]] = None,
    ):
        self.name: str = validate_context_menu_name(name)
        self._callback: ContextMenuCallback = callback
        (param, annotation, actual_type) = _get_context_menu_parameter(callback)
        if type is MISSING:
            type = actual_type

        if actual_type != type:
            raise ValueError(f'context menu callback implies a type of {actual_type} but {type} was passed.')

        self.type: AppCommandType = type
        self._param_name = param
        self._annotation = annotation
        self.module: Optional[str] = callback.__module__
        self._guild_ids = guild_ids or getattr(callback, '__discord_app_commands_default_guilds__', None)
        self.on_error: Optional[UnboundError] = None
        self.default_permissions: Optional[Permissions] = getattr(
            callback, '__discord_app_commands_default_permissions__', None
        )
        self.guild_only: bool = getattr(callback, '__discord_app_commands_guild_only__', False)
        self.checks: List[Check] = getattr(callback, '__discord_app_commands_checks__', [])

    @property
    def callback(self) -> ContextMenuCallback:
        """:ref:`coroutine <coroutine>`: The coroutine that is executed when the context menu is called."""
        return self._callback

    @property
    def qualified_name(self) -> str:
        """:class:`str`: Returns the fully qualified command name."""
        return self.name

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.type.value,
            'dm_permission': not self.guild_only,
            'default_member_permissions': self.default_permissions and self.default_permissions.value,
        }

    async def _check_can_run(self, interaction: Interaction) -> bool:
        predicates = self.checks
        if not predicates:
            return True

        # Type checker does not understand negative narrowing cases like this function
        return await async_all(f(interaction) for f in predicates)  # type: ignore

    def _has_any_error_handlers(self) -> bool:
        return self.on_error is not None

    async def _invoke(self, interaction: Interaction, arg: Any):
        try:
            if not await self._check_can_run(interaction):
                raise CheckFailure(f'The check functions for context menu {self.name!r} failed.')

            await self._callback(interaction, arg)
        except AppCommandError:
            raise
        except Exception as e:
            raise CommandInvokeError(self, e) from e

    def error(self, coro: UnboundError) -> UnboundError:
        """A decorator that registers a coroutine as a local error handler.

        The local error handler is called whenever an exception is raised in the body
        of the command or during handling of the command. The error handler must take
        2 parameters, the interaction and the error.

        The error passed will be derived from :exc:`AppCommandError`.

        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the local error handler.

        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """

        if not inspect.iscoroutinefunction(coro):
            raise TypeError('The error handler must be a coroutine.')

        self.on_error = coro
        return coro

    def add_check(self, func: Check, /) -> None:
        """Adds a check to the command.

        This is the non-decorator interface to :func:`check`.

        Parameters
        -----------
        func
            The function that will be used as a check.
        """

        self.checks.append(func)

    def remove_check(self, func: Check, /) -> None:
        """Removes a check from the command.

        This function is idempotent and will not raise an exception
        if the function is not in the command's checks.

        Parameters
        -----------
        func
            The function to remove from the checks.
        """

        try:
            self.checks.remove(func)
        except ValueError:
            pass


class Group:
    """A class that implements an application command group.

    These are usually inherited rather than created manually.

    Decorators such as :func:`guild_only`, :func:`guilds`, and :func:`default_permissions`
    will apply to the group if used on top of a subclass. For example:

    .. code-block:: python3

        from discord import app_commands

        @app_commands.guild_only()
        class MyGroup(app_commands.Group):
            pass

    .. versionadded:: 2.0

    Attributes
    ------------
    name: :class:`str`
        The name of the group. If not given, it defaults to a lower-case
        kebab-case version of the class name.
    description: :class:`str`
        The description of the group. This shows up in the UI to describe
        the group. If not given, it defaults to the docstring of the
        class shortened to 100 characters.
    default_permissions: Optional[:class:`~discord.Permissions`]
        The default permissions that can execute this group on Discord. Note
        that server administrators can override this value in the client.
        Setting an empty permissions field will disallow anyone except server
        administrators from using the command in a guild.

        Due to a Discord limitation, this does not work on subcommands.
    guild_only: :class:`bool`
        Whether the group should only be usable in guild contexts.
        Defaults to ``False``.

        Due to a Discord limitation, this does not work on subcommands.
    parent: Optional[:class:`Group`]
        The parent group. ``None`` if there isn't one.
    """

    __discord_app_commands_group_children__: ClassVar[List[Union[Command[Any, ..., Any], Group]]] = []
    __discord_app_commands_skip_init_binding__: bool = False
    __discord_app_commands_group_name__: str = MISSING
    __discord_app_commands_group_description__: str = MISSING
    __discord_app_commands_guild_only__: bool = MISSING
    __discord_app_commands_default_permissions__: Optional[Permissions] = MISSING
    __discord_app_commands_has_module__: bool = False

    def __init_subclass__(
        cls,
        *,
        name: str = MISSING,
        description: str = MISSING,
        guild_only: bool = MISSING,
        default_permissions: Optional[Permissions] = MISSING,
    ) -> None:
        if not cls.__discord_app_commands_group_children__:
            children: List[Union[Command[Any, ..., Any], Group]] = [
                member for member in cls.__dict__.values() if isinstance(member, (Group, Command)) and member.parent is None
            ]

            cls.__discord_app_commands_group_children__ = children

            found = set()
            for child in children:
                if child.name in found:
                    raise TypeError(f'Command {child.name!r} is a duplicate')
                found.add(child.name)

            if len(children) > 25:
                raise TypeError('groups cannot have more than 25 commands')

        if name is MISSING:
            cls.__discord_app_commands_group_name__ = validate_name(_to_kebab_case(cls.__name__))
        else:
            cls.__discord_app_commands_group_name__ = validate_name(name)

        if description is MISSING:
            if cls.__doc__ is None:
                cls.__discord_app_commands_group_description__ = '…'
            else:
                cls.__discord_app_commands_group_description__ = _shorten(cls.__doc__)
        else:
            cls.__discord_app_commands_group_description__ = description

        if guild_only is not MISSING:
            cls.__discord_app_commands_guild_only__ = guild_only

        if default_permissions is not MISSING:
            cls.__discord_app_commands_default_permissions__ = default_permissions

        if cls.__module__ != __name__:
            cls.__discord_app_commands_has_module__ = True

    def __init__(
        self,
        *,
        name: str = MISSING,
        description: str = MISSING,
        parent: Optional[Group] = None,
        guild_ids: Optional[List[int]] = None,
        guild_only: bool = MISSING,
        default_permissions: Optional[Permissions] = MISSING,
    ):
        cls = self.__class__
        self.name: str = validate_name(name) if name is not MISSING else cls.__discord_app_commands_group_name__
        self.description: str = description or cls.__discord_app_commands_group_description__
        self._attr: Optional[str] = None
        self._owner_cls: Optional[Type[Any]] = None
        self._guild_ids: Optional[List[int]] = guild_ids or getattr(cls, '__discord_app_commands_default_guilds__', None)

        if default_permissions is MISSING:
            if cls.__discord_app_commands_default_permissions__ is MISSING:
                default_permissions = None
            else:
                default_permissions = cls.__discord_app_commands_default_permissions__

        self.default_permissions: Optional[Permissions] = default_permissions

        if guild_only is MISSING:
            if cls.__discord_app_commands_guild_only__ is MISSING:
                guild_only = False
            else:
                guild_only = cls.__discord_app_commands_guild_only__

        self.guild_only: bool = guild_only

        if not self.description:
            raise TypeError('groups must have a description')

        self.parent: Optional[Group] = parent
        self.module: Optional[str]
        if cls.__discord_app_commands_has_module__:
            self.module = cls.__module__
        else:
            try:
                # This is pretty hacky
                # It allows the module to be fetched if someone just constructs a bare Group object though.
                self.module = inspect.currentframe().f_back.f_globals['__name__']  # type: ignore
            except (AttributeError, IndexError):
                self.module = None

        self._children: Dict[str, Union[Command, Group]] = {}

        bindings: Dict[Group, Group] = {}

        for child in self.__discord_app_commands_group_children__:
            # commands and groups created directly in this class (no parent)
            copy = (
                child._copy_with(parent=self, binding=self, bindings=bindings, set_on_binding=False)
                if not cls.__discord_app_commands_skip_init_binding__
                else child
            )

            self._children[copy.name] = copy
            if copy._attr and not cls.__discord_app_commands_skip_init_binding__:
                setattr(self, copy._attr, copy)

        if parent is not None:
            if parent.parent is not None:
                raise ValueError('groups can only be nested at most one level')
            parent.add_command(self)

    def __set_name__(self, owner: Type[Any], name: str) -> None:
        self._attr = name
        self.module = owner.__module__
        self._owner_cls = owner

    def _copy_with(
        self,
        *,
        parent: Optional[Group],
        binding: Binding,
        bindings: MutableMapping[Group, Group] = MISSING,
        set_on_binding: bool = True,
    ) -> Group:
        bindings = {} if bindings is MISSING else bindings

        cls = self.__class__
        copy = cls.__new__(cls)
        copy.name = self.name
        copy._guild_ids = self._guild_ids
        copy.description = self.description
        copy.parent = parent
        copy.module = self.module
        copy.default_permissions = self.default_permissions
        copy.guild_only = self.guild_only
        copy._attr = self._attr
        copy._owner_cls = self._owner_cls
        copy._children = {}

        bindings[self] = copy

        for child in self._children.values():
            child_copy = child._copy_with(parent=copy, binding=binding, bindings=bindings)
            child_copy.parent = copy
            copy._children[child_copy.name] = child_copy

            if isinstance(child_copy, Group) and child_copy._attr and set_on_binding:
                if binding.__class__ is child_copy._owner_cls:
                    setattr(binding, child_copy._attr, child_copy)
                elif child_copy._owner_cls is copy.__class__:
                    setattr(copy, child_copy._attr, child_copy)

        if copy._attr and set_on_binding:
            setattr(parent or binding, copy._attr, copy)

        return copy

    def to_dict(self) -> Dict[str, Any]:
        # If this has a parent command then it's part of a subcommand group
        # Otherwise, it's just a regular command
        option_type = 1 if self.parent is None else AppCommandOptionType.subcommand_group.value
        base: Dict[str, Any] = {
            'name': self.name,
            'description': self.description,
            'type': option_type,
            'options': [child.to_dict() for child in self._children.values()],
        }

        if self.parent is None:
            base['dm_permission'] = not self.guild_only
            base['default_member_permissions'] = self.default_permissions and self.default_permissions.value

        return base

    @property
    def root_parent(self) -> Optional[Group]:
        """Optional[:class:`Group`]: The parent of this group."""
        return self.parent

    @property
    def qualified_name(self) -> str:
        """:class:`str`: Returns the fully qualified group name.

        The qualified name includes the parent name as well. For example,
        in a group like ``/foo bar`` the qualified name is ``foo bar``.
        """

        if self.parent is None:
            return self.name
        return f'{self.parent.name} {self.name}'

    def _get_internal_command(self, name: str) -> Optional[Union[Command[Any, ..., Any], Group]]:
        return self._children.get(name)

    @property
    def commands(self) -> List[Union[Command[Any, ..., Any], Group]]:
        """List[Union[:class:`Command`, :class:`Group`]]: The commands that this group contains."""
        return list(self._children.values())

    def walk_commands(self) -> Generator[Union[Command[Any, ..., Any], Group], None, None]:
        """An iterator that recursively walks through all commands that this group contains.

        Yields
        ---------
        Union[:class:`Command`, :class:`Group`]
            The commands in this group.
        """

        for command in self._children.values():
            yield command
            if isinstance(command, Group):
                yield from command.walk_commands()

    async def on_error(self, interaction: Interaction, error: AppCommandError) -> None:
        """|coro|

        A callback that is called when a child's command raises an :exc:`AppCommandError`.

        To get the command that failed, :attr:`discord.Interaction.command` should be used.

        The default implementation does nothing.

        Parameters
        -----------
        interaction: :class:`~discord.Interaction`
            The interaction that is being handled.
        error: :exc:`AppCommandError`
            The exception that was raised.
        """

        pass

    def error(self, coro: ErrorFunc) -> ErrorFunc:
        """A decorator that registers a coroutine as a local error handler.

        The local error handler is called whenever an exception is raised in a child command.
        The error handler must take 2 parameters, the interaction and the error.

        The error passed will be derived from :exc:`AppCommandError`.

        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the local error handler.

        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine, or is an invalid coroutine.
        """

        if not inspect.iscoroutinefunction(coro):
            raise TypeError('The error handler must be a coroutine.')

        params = inspect.signature(coro).parameters
        if len(params) != 2:
            raise TypeError('The error handler must have 2 parameters.')

        self.on_error = coro  # type: ignore
        return coro

    async def interaction_check(self, interaction: Interaction) -> bool:
        """|coro|

        A callback that is called when an interaction happens within the group
        that checks whether a command inside the group should be executed.

        This is useful to override if, for example, you want to ensure that the
        interaction author is a given user.

        The default implementation of this returns ``True``.

        .. note::

            If an exception occurs within the body then the check
            is considered a failure and error handlers such as
            :meth:`on_error` is called. See :exc:`AppCommandError`
            for more information.

        Parameters
        -----------
        interaction: :class:`~discord.Interaction`
            The interaction that occurred.

        Returns
        ---------
        :class:`bool`
            Whether the view children's callbacks should be called.
        """

        return True

    def add_command(self, command: Union[Command[Any, ..., Any], Group], /, *, override: bool = False) -> None:
        """Adds a command or group to this group's internal list of commands.

        Parameters
        -----------
        command: Union[:class:`Command`, :class:`Group`]
            The command or group to add.
        override: :class:`bool`
            Whether to override a pre-existing command or group with the same name.
            If ``False`` then an exception is raised.

        Raises
        -------
        CommandAlreadyRegistered
            The command or group is already registered. Note that the :attr:`CommandAlreadyRegistered.guild_id`
            attribute will always be ``None`` in this case.
        ValueError
            There are too many commands already registered or the group is too
            deeply nested.
        TypeError
            The wrong command type was passed.
        """

        if not isinstance(command, (Command, Group)):
            raise TypeError(f'expected Command or Group not {command.__class__!r}')

        if isinstance(command, Group) and self.parent is not None:
            # In a tree like so:
            # <group>
            #   <self>
            #     <group>
            # this needs to be forbidden
            raise ValueError(f'{command.name!r} is too nested, groups can only be nested at most one level')

        if not override and command.name in self._children:
            raise CommandAlreadyRegistered(command.name, guild_id=None)

        self._children[command.name] = command
        command.parent = self
        if len(self._children) > 25:
            raise ValueError('maximum number of child commands exceeded')

    def remove_command(self, name: str, /) -> Optional[Union[Command[Any, ..., Any], Group]]:
        """Removes a command or group from the internal list of commands.

        Parameters
        -----------
        name: :class:`str`
            The name of the command or group to remove.

        Returns
        --------
        Optional[Union[:class:`~discord.app_commands.Command`, :class:`~discord.app_commands.Group`]]
            The command that was removed. If nothing was removed
            then ``None`` is returned instead.
        """

        self._children.pop(name, None)

    def get_command(self, name: str, /) -> Optional[Union[Command[Any, ..., Any], Group]]:
        """Retrieves a command or group from its name.

        Parameters
        -----------
        name: :class:`str`
            The name of the command or group to retrieve.

        Returns
        --------
        Optional[Union[:class:`~discord.app_commands.Command`, :class:`~discord.app_commands.Group`]]
            The command or group that was retrieved. If nothing was found
            then ``None`` is returned instead.
        """
        return self._children.get(name)

    def command(
        self,
        *,
        name: str = MISSING,
        description: str = MISSING,
    ) -> Callable[[CommandCallback[GroupT, P, T]], Command[GroupT, P, T]]:
        """Creates an application command under this group.

        Parameters
        ------------
        name: :class:`str`
            The name of the application command. If not given, it defaults to a lower-case
            version of the callback name.
        description: :class:`str`
            The description of the application command. This shows up in the UI to describe
            the application command. If not given, it defaults to the first line of the docstring
            of the callback shortened to 100 characters.
        """

        def decorator(func: CommandCallback[GroupT, P, T]) -> Command[GroupT, P, T]:
            if not inspect.iscoroutinefunction(func):
                raise TypeError('command function must be a coroutine function')

            if description is MISSING:
                if func.__doc__ is None:
                    desc = '…'
                else:
                    desc = _shorten(func.__doc__)
            else:
                desc = description

            command = Command(
                name=name if name is not MISSING else func.__name__,
                description=desc,
                callback=func,
                parent=self,
            )
            self.add_command(command)
            return command

        return decorator


def command(
    *,
    name: str = MISSING,
    description: str = MISSING,
) -> Callable[[CommandCallback[GroupT, P, T]], Command[GroupT, P, T]]:
    """Creates an application command from a regular function.

    Parameters
    ------------
    name: :class:`str`
        The name of the application command. If not given, it defaults to a lower-case
        version of the callback name.
    description: :class:`str`
        The description of the application command. This shows up in the UI to describe
        the application command. If not given, it defaults to the first line of the docstring
        of the callback shortened to 100 characters.
    """

    def decorator(func: CommandCallback[GroupT, P, T]) -> Command[GroupT, P, T]:
        if not inspect.iscoroutinefunction(func):
            raise TypeError('command function must be a coroutine function')

        if description is MISSING:
            if func.__doc__ is None:
                desc = '…'
            else:
                desc = _shorten(func.__doc__)
        else:
            desc = description

        return Command(
            name=name if name is not MISSING else func.__name__,
            description=desc,
            callback=func,
            parent=None,
        )

    return decorator


def context_menu(*, name: str = MISSING) -> Callable[[ContextMenuCallback], ContextMenu]:
    """Creates an application command context menu from a regular function.

    This function must have a signature of :class:`~discord.Interaction` as its first parameter
    and taking either a :class:`~discord.Member`, :class:`~discord.User`, or :class:`~discord.Message`,
    or a :obj:`typing.Union` of ``Member`` and ``User`` as its second parameter.

    Examples
    ---------

    .. code-block:: python3

        @app_commands.context_menu()
        async def react(interaction: discord.Interaction, message: discord.Message):
            await interaction.response.send_message('Very cool message!', ephemeral=True)

        @app_commands.context_menu()
        async def ban(interaction: discord.Interaction, user: discord.Member):
            await interaction.response.send_message(f'Should I actually ban {user}...', ephemeral=True)

    Parameters
    ------------
    name: :class:`str`
        The name of the context menu command. If not given, it defaults to a title-case
        version of the callback name. Note that unlike regular slash commands this can
        have spaces and upper case characters in the name.
    """

    def decorator(func: ContextMenuCallback) -> ContextMenu:
        if not inspect.iscoroutinefunction(func):
            raise TypeError('context menu function must be a coroutine function')

        actual_name = func.__name__.title() if name is MISSING else name
        return ContextMenu(name=actual_name, callback=func)

    return decorator


def describe(**parameters: str) -> Callable[[T], T]:
    r"""Describes the given parameters by their name using the key of the keyword argument
    as the name.

    Example:

    .. code-block:: python3

        @app_commands.command()
        @app_commands.describe(member='the member to ban')
        async def ban(interaction: discord.Interaction, member: discord.Member):
            await interaction.response.send_message(f'Banned {member}')

    Parameters
    -----------
    \*\*parameters
        The description of the parameters.

    Raises
    --------
    TypeError
        The parameter name is not found.
    """

    def decorator(inner: T) -> T:
        if isinstance(inner, Command):
            _populate_descriptions(inner._params, parameters)
        else:
            try:
                inner.__discord_app_commands_param_description__.update(parameters)  # type: ignore # Runtime attribute access
            except AttributeError:
                inner.__discord_app_commands_param_description__ = parameters  # type: ignore # Runtime attribute assignment

        return inner

    return decorator


def rename(**parameters: str) -> Callable[[T], T]:
    r"""Renames the given parameters by their name using the key of the keyword argument
    as the name.

    Example:

    .. code-block:: python3

        @app_commands.command()
        @app_commands.rename(the_member_to_ban='member')
        async def ban(interaction: discord.Interaction, the_member_to_ban: discord.Member):
            await interaction.response.send_message(f'Banned {the_member_to_ban}')

    Parameters
    -----------
    \*\*parameters
        The name of the parameters.

    Raises
    --------
    ValueError
        The parameter name is already used by another parameter.
    TypeError
        The parameter name is not found.
    """

    def decorator(inner: T) -> T:
        if isinstance(inner, Command):
            _populate_renames(inner._params, parameters)
        else:
            try:
                inner.__discord_app_commands_param_rename__.update(parameters)  # type: ignore # Runtime attribute access
            except AttributeError:
                inner.__discord_app_commands_param_rename__ = parameters  # type: ignore # Runtime attribute assignment

        return inner

    return decorator


def choices(**parameters: List[Choice[ChoiceT]]) -> Callable[[T], T]:
    r"""Instructs the given parameters by their name to use the given choices for their choices.

    Example:

    .. code-block:: python3

        @app_commands.command()
        @app_commands.describe(fruits='fruits to choose from')
        @app_commands.choices(fruits=[
            Choice(name='apple', value=1),
            Choice(name='banana', value=2),
            Choice(name='cherry', value=3),
        ])
        async def fruit(interaction: discord.Interaction, fruits: Choice[int]):
            await interaction.response.send_message(f'Your favourite fruit is {fruits.name}.')

    .. note::

        This is not the only way to provide choices to a command. There are two more ergonomic ways
        of doing this. The first one is to use a :obj:`typing.Literal` annotation:

        .. code-block:: python3

            @app_commands.command()
            @app_commands.describe(fruits='fruits to choose from')
            async def fruit(interaction: discord.Interaction, fruits: Literal['apple', 'banana', 'cherry']):
                await interaction.response.send_message(f'Your favourite fruit is {fruits}.')

        The second way is to use an :class:`enum.Enum`:

        .. code-block:: python3

            class Fruits(enum.Enum):
                apple = 1
                banana = 2
                cherry = 3

            @app_commands.command()
            @app_commands.describe(fruits='fruits to choose from')
            async def fruit(interaction: discord.Interaction, fruits: Fruits):
                await interaction.response.send_message(f'Your favourite fruit is {fruits}.')


    Parameters
    -----------
    \*\*parameters
        The choices of the parameters.

    Raises
    --------
    TypeError
        The parameter name is not found or the parameter type was incorrect.
    """

    def decorator(inner: T) -> T:
        if isinstance(inner, Command):
            _populate_choices(inner._params, parameters)
        else:
            try:
                inner.__discord_app_commands_param_choices__.update(parameters)  # type: ignore # Runtime attribute access
            except AttributeError:
                inner.__discord_app_commands_param_choices__ = parameters  # type: ignore # Runtime attribute assignment

        return inner

    return decorator


def autocomplete(**parameters: AutocompleteCallback[GroupT, ChoiceT]) -> Callable[[T], T]:
    r"""Associates the given parameters with the given autocomplete callback.

    Autocomplete is only supported on types that have :class:`str`, :class:`int`, or :class:`float`
    values.

    :func:`Checks <check>` are supported, however they must be attached to the autocomplete
    callback in order to work. Checks attached to the command are ignored when invoking the autocomplete
    callback.

    For more information, see the :meth:`Command.autocomplete` documentation.

    Example:

    .. code-block:: python3

            @app_commands.command()
            @app_commands.autocomplete(fruit=fruit_autocomplete)
            async def fruits(interaction: discord.Interaction, fruit: str):
                await interaction.response.send_message(f'Your favourite fruit seems to be {fruit}')

            async def fruit_autocomplete(
                interaction: discord.Interaction,
                current: str,
            ) -> List[app_commands.Choice[str]]:
                fruits = ['Banana', 'Pineapple', 'Apple', 'Watermelon', 'Melon', 'Cherry']
                return [
                    app_commands.Choice(name=fruit, value=fruit)
                    for fruit in fruits if current.lower() in fruit.lower()
                ]

    Parameters
    -----------
    \*\*parameters
        The parameters to mark as autocomplete.

    Raises
    --------
    TypeError
        The parameter name is not found or the parameter type was incorrect.
    """

    def decorator(inner: T) -> T:
        if isinstance(inner, Command):
            _populate_autocomplete(inner._params, parameters)
        else:
            try:
                inner.__discord_app_commands_param_autocomplete__.update(parameters)  # type: ignore # Runtime attribute access
            except AttributeError:
                inner.__discord_app_commands_param_autocomplete__ = parameters  # type: ignore # Runtime attribute assignment

        return inner

    return decorator


def guilds(*guild_ids: Union[Snowflake, int]) -> Callable[[T], T]:
    r"""Associates the given guilds with the command.

    When the command instance is added to a :class:`CommandTree`, the guilds that are
    specified by this decorator become the default guilds that it's added to rather
    than being a global command.

    .. note::

        Due to an implementation quirk and Python limitation, if this is used in conjunction
        with the :meth:`CommandTree.command` or :meth:`CommandTree.context_menu` decorator
        then this must go below that decorator.

    Example:

    .. code-block:: python3

            MY_GUILD_ID = discord.Object(...)  # Guild ID here

            @app_commands.command()
            @app_commands.guilds(MY_GUILD_ID)
            async def bonk(interaction: discord.Interaction):
                await interaction.response.send_message('Bonk', ephemeral=True)

    Parameters
    -----------
    \*guild_ids: Union[:class:`int`, :class:`~discord.abc.Snowflake`]
        The guilds to associate this command with. The command tree will
        use this as the default when added rather than adding it as a global
        command.
    """

    defaults: List[int] = [g if isinstance(g, int) else g.id for g in guild_ids]

    def decorator(inner: T) -> T:
        if isinstance(inner, (Group, ContextMenu)):
            inner._guild_ids = defaults
        elif isinstance(inner, Command):
            if inner.parent is not None:
                raise ValueError('child commands of a group cannot have default guilds set')

            inner._guild_ids = defaults
        else:
            # Runtime attribute assignment
            inner.__discord_app_commands_default_guilds__ = defaults  # type: ignore

        return inner

    return decorator


def check(predicate: Check) -> Callable[[T], T]:
    r"""A decorator that adds a check to an application command.

    These checks should be predicates that take in a single parameter taking
    a :class:`~discord.Interaction`. If the check returns a ``False``\-like value then
    during invocation a :exc:`CheckFailure` exception is raised and sent to
    the appropriate error handlers.

    These checks can be either a coroutine or not.

    Examples
    ---------

    Creating a basic check to see if the command invoker is you.

    .. code-block:: python3

        def check_if_it_is_me(interaction: discord.Interaction) -> bool:
            return interaction.user.id == 85309593344815104

        @tree.command()
        @app_commands.check(check_if_it_is_me)
        async def only_for_me(interaction: discord.Interaction):
            await interaction.response.send_message('I know you!', ephemeral=True)

    Transforming common checks into its own decorator:

    .. code-block:: python3

        def is_me():
            def predicate(interaction: discord.Interaction) -> bool:
                return interaction.user.id == 85309593344815104
            return app_commands.check(predicate)

        @tree.command()
        @is_me()
        async def only_me(interaction: discord.Interaction):
            await interaction.response.send_message('Only you!')

    Parameters
    -----------
    predicate: Callable[[:class:`~discord.Interaction`], :class:`bool`]
        The predicate to check if the command should be invoked.
    """

    def decorator(func: CheckInputParameter) -> CheckInputParameter:
        if isinstance(func, (Command, ContextMenu)):
            func.checks.append(predicate)
        else:
            if not hasattr(func, '__discord_app_commands_checks__'):
                func.__discord_app_commands_checks__ = []

            func.__discord_app_commands_checks__.append(predicate)

        return func

    return decorator  # type: ignore


@overload
def guild_only(func: None = ...) -> Callable[[T], T]:
    ...


@overload
def guild_only(func: T) -> T:
    ...


def guild_only(func: Optional[T] = None) -> Union[T, Callable[[T], T]]:
    """A decorator that indicates this command can only be used in a guild context.

    This is **not** implemented as a :func:`check`, and is instead verified by Discord server side.
    Therefore, there is no error handler called when a command is used within a private message.

    This decorator can be called with or without parentheses.

    Due to a Discord limitation, this decorator does nothing in subcommands and is ignored.

    Examples
    ---------

    .. code-block:: python3

        @app_commands.command()
        @app_commands.guild_only()
        async def my_guild_only_command(interaction: discord.Interaction) -> None:
            await interaction.response.send_message('I am only available in guilds!')
    """

    def inner(f: T) -> T:
        if isinstance(f, (Command, Group, ContextMenu)):
            f.guild_only = True
        else:
            f.__discord_app_commands_guild_only__ = True  # type: ignore # Runtime attribute assignment
        return f

    # Check if called with parentheses or not
    if func is None:
        # Called with parentheses
        return inner
    else:
        return inner(func)


def default_permissions(**perms: bool) -> Callable[[T], T]:
    r"""A decorator that sets the default permissions needed to execute this command.

    When this decorator is used, by default users must have these permissions to execute the command.
    However, an administrator can change the permissions needed to execute this command using the official
    client. Therefore, this only serves as a hint.

    Setting an empty permissions field, including via calling this with no arguments, will disallow anyone
    except server administrators from using the command in a guild.

    This is sent to Discord server side, and is not a :func:`check`. Therefore, error handlers are not called.

    Due to a Discord limitation, this decorator does nothing in subcommands and is ignored.

    .. warning::

        This serves as a *hint* and members are *not* required to have the permissions given to actually
        execute this command. If you want to ensure that members have the permissions needed, consider using
        :func:`~discord.app_commands.checks.has_permissions` instead.

    Parameters
    -----------
    \*\*perms: :class:`bool`
        Keyword arguments denoting the permissions to set as the default.

    Example
    ---------

    .. code-block:: python3

        @app_commands.command()
        @app_commands.default_permissions(manage_messages=True)
        async def test(interaction: discord.Interaction):
            await interaction.response.send_message('You may or may not have manage messages.')
    """

    permissions = Permissions(**perms)

    def decorator(func: T) -> T:
        if isinstance(func, (Command, Group, ContextMenu)):
            func.default_permissions = permissions
        else:
            func.__discord_app_commands_default_permissions__ = permissions  # type: ignore # Runtime attribute assignment

        return func

    return decorator
