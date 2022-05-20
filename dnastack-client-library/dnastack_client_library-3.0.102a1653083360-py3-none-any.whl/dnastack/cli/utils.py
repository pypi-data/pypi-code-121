import click
import inspect
import json
import logging
import re
import sys
from click import UsageError, Option, Group
from pydantic import BaseModel
from typing import Any, List, Callable, Tuple, Mapping, Optional, Union, Dict

from ..common.logger import get_logger
from ..feature_flags import in_global_debug_mode


# CLICK EXTENSIONS
class MutuallyExclusiveOption(Option):
    """
    A click Option wrapper for sets of options where one but not both must be specified
    """

    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop("mutually_exclusive", []))
        original_help = kwargs.get("help", "")
        if self.mutually_exclusive:
            additional_help_text = "This is mutually exclusive with " \
                                   + " and ".join(sorted(self.mutually_exclusive)) + "."
            kwargs[
                "help"] = f"{original_help}. Note that {additional_help_text}" if original_help else additional_help_text
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx: click.Context, opts: Mapping[str, Any], args: List[str]) -> Tuple[
        Any, List[str]]:
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise UsageError(
                "Illegal usage: `{}` is mutually exclusive with "
                "arguments `{}`.".format(self.name, ", ".join(self.mutually_exclusive))
            )

        return super(MutuallyExclusiveOption, self).handle_parse_result(ctx, opts, args)


def parse_key_value_param(parameter: str, param_name: str) -> str:
    """Parse a parameters specified in a K=V format and dumps to a JSON str"""
    param_key_value = parameter.split("=")

    if len(param_key_value) != 2:
        click.secho(
            f"Invalid format for {param_name}. Must be a single key-value pair in the format K=V",
            fg="red",
        )
        sys.exit(1)

    return json.dumps({param_key_value[0].strip(): param_key_value[1].strip()})


def handle_error_gracefully(command: Callable) -> Callable:
    """
    Handle error gracefully

    This is disabled in the debug mode.
    """

    def handle_invocation(*args, **kwargs):
        if in_global_debug_mode:
            # In the debug mode, no error will be handled gracefully so that the developers can see the full detail.
            command(*args, **kwargs)
        else:
            try:
                command(*args, **kwargs)
            except Exception as e:
                click.secho(e, fg="red")
                sys.exit(1)

    handle_invocation.__doc__ = command.__doc__

    return handle_invocation


def allow_to_specify_endpoint(handler: Callable) -> Callable:
    click.option('--endpoint-id',
                 help='Service Endpoint ID',
                 required=False,
                 default=None)(handler)
    click.option('--endpoint-url',
                 help='Service Endpoint URL',
                 required=False,
                 default=None)(handler)
    return handler


class ArgumentSpec(BaseModel):
    """
    Argument specification

    This is designed to use with @command where you want to customize how it automatically maps the callable's arguments
    as the command arguments/options.
    """
    name: str
    arg_names: Optional[List[str]]
    as_option: bool = False
    help: Optional[str]
    choices: Optional[List]
    ignored: bool = False
    for_fixed_spec_only__required: Optional[bool]

    # NOTE: the "type" and "default value" can be determined via the reflection if implemented.


def command(command_group: Group,
            alternate_command_name: Optional[str] = None,
            specs: List[Union[ArgumentSpec, Dict[str, Any]]] = None,
            excluded_arguments: List[str] = None,
            allow_to_specify_endpoint: bool = False,
            setup_debug_enabled: bool = False):
    """
    Set up a basic command and automatically configure CLI arguments or options based on the signature
    of the handler (given callable).

    :param command_group: the command group
    :param alternate_command_name: the alternate command name - by default, the command name is derived from the name
                                   of the annotated/decorated callable.
    :param specs: Overriding argument/option specifications - by default, this decorator will automatically set any
                  callable's arguments as CLI in-line arguments.
    :param excluded_arguments: The list of callable's arguments to ignore from the autoconfiguration.
    """
    _logger = get_logger('@command', logging.DEBUG) if setup_debug_enabled else get_logger('@command')

    argument_specs = [(ArgumentSpec(**spec) if isinstance(spec, dict) else spec)
                      for spec in (specs or list())]

    argument_specs.append(ArgumentSpec(
        name='endpoint_id',
        arg_names=['--endpoint-id'],
        as_option=True,
        help='Endpoint ID',
        for_fixed_spec_only__required=False,
    ))

    # This is for the future implementation.
    argument_specs.append(ArgumentSpec(
        name='endpoint_url',
        arg_names=['--endpoint-url'],
        as_option=True,
        help='Endpoint URL',
        for_fixed_spec_only__required=False,
    ))

    argument_spec_map: Dict[str, ArgumentSpec] = {spec.name: spec for spec in argument_specs}

    excluded_argument_names = excluded_arguments or list()
    for spec in argument_spec_map.values():
        if spec.ignored:
            excluded_argument_names.append(spec.name)

    def decorator(handler: Callable):
        command_name = alternate_command_name if alternate_command_name else re.sub(r'_', '-', handler.__name__)

        handler_signature = inspect.signature(handler)

        def handle_invocation(*args, **kwargs):
            if in_global_debug_mode:
                # In the debug mode, no error will be handled gracefully so that the developers can see the full detail.
                handler(*args, **kwargs)
            else:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    error_type = type(e).__name__
                    error_type = re.sub(r'([A-Z])', r' \1', error_type).strip()
                    error_type = re.sub(r' Error$', r'', error_type).strip().capitalize()

                    click.secho(f'{error_type}: ', dim=True, nl=False)
                    click.secho(e, fg="red")

                    sys.exit(1)

        handle_invocation.__doc__ = handler.__doc__

        command_obj = command_group.command(command_name)(handle_invocation)

        for param_name, param in handler_signature.parameters.items():
            if param_name in excluded_argument_names:
                continue

            required = True
            default_value = None

            annotation = param.annotation
            if annotation is None or annotation == inspect._empty:
                param_type = str
            elif inspect.isclass(annotation):
                param_type = annotation
            else:
                if sys.version_info >= (3, 8):
                    ##################################
                    # To support Python 3.8 or newer #
                    ##################################

                    from typing import get_origin, get_args
                    special_type = get_origin(annotation)
                    type_args = get_args(annotation)

                    if special_type is Union:
                        param_type = [t for t in type_args if t is not None][0]
                        required = type(None) not in type_args
                    else:
                        raise RuntimeError(f'Programming Error: The type of parameter {param_name} ({annotation}) is '
                                           f'not supported by this decorator. Please contact the technical support.')
                else:
                    ##################################
                    # To support Python 3.7 or older #
                    ##################################
                    if str(annotation).startswith('typing.Union[') and 'NoneType' in str(annotation):
                        # To keep this simple, the union annotation with none type is assumed
                        # to be for an optional string argument. Python 3.8 code branch can
                        # detect the type better.
                        param_type = str
                        required = False
                    else:
                        raise RuntimeError(f'Programming Error: The type of parameter {param_name} ({annotation}) is '
                                           f'not supported by this decorator. Please contact the technical support.')

            if param.default != inspect._empty:
                default_value = param.default
                required = False

            additional_specs = dict(type=param_type,
                                    required=required,
                                    default=default_value)

            if param_name in argument_spec_map:
                spec = argument_spec_map[param_name]

                _logger.debug(f'C/{command_obj}: SPEC: {spec}')

                if spec.for_fixed_spec_only__required is not None:
                    required = spec.for_fixed_spec_only__required

                input_names = []
                if spec.arg_names:
                    input_names.extend(spec.arg_names)
                input_names.append(param_name)

                if spec.help:
                    additional_specs['help'] = spec.help

                if spec.choices:
                    additional_specs.update({
                        'type': click.Choice(spec.choices),
                        'show_choices': True,
                    })

                additional_specs.update({
                    'required': required,
                    'show_default': not required,
                })

                _logger.debug(f'C/{command_obj}: {"OPT" if spec.as_option else "ARG"} ({input_names}, {additional_specs})')

                (click.option if spec.as_option else click.argument)(*input_names, **additional_specs)(command_obj)
            else:
                click.argument(param_name, **additional_specs)(command_obj)

        if allow_to_specify_endpoint:
            click.option('--endpoint-id',
                         help='Service Endpoint ID',
                         required=False,
                         default=None)(command_obj)
            click.option('--endpoint-url',
                         help='Service Endpoint URL',
                         required=False,
                         default=None)(command_obj)

        _logger.debug(f'C/{command_obj}: Setup complete')

        return command_obj

    return decorator


def echo_header(title: str, bg: str = 'blue', fg: str = 'white'):
    vertical_padding = ' ' * (len(title) + 4)

    print()
    click.secho(vertical_padding, bold=True, bg=bg, fg=fg)
    click.secho(f'  {title}  ', bold=True, bg=bg, fg=fg)
    click.secho(vertical_padding, bold=True, bg=bg, fg=fg)
    print()


def show_alternative_for_deprecated_command(alternative: Optional[str]):
    bg_color = 'yellow'
    fg_color = 'white'

    if alternative:
        echo_header(f'WARNING: Please use "{alternative}" instead.', bg_color, fg_color)
    else:
        echo_header('WARNING: No alternative to this command.', bg_color, fg_color)
