import functools
import sys
from dataclasses import dataclass
from typing import Callable
from typing import List
from typing import Optional

import click
import pendulum

from tecton._internals.analytics import AnalyticsLogger
from tecton.cli import common
from tecton.cli import printer
from tecton_spark import conf

analytics = AnalyticsLogger()


def _cluster_url() -> Optional[str]:
    from tecton import conf

    api_service = conf.get_or_none("API_SERVICE")
    if api_service:
        # API_SERVICE URLs of the form <subdomain>.tecton.ai/api are expected so this check
        # ensures an internal DNS address isn't being used or an invalid path is specified.
        if api_service.endswith("/api") and "ingress" not in api_service:
            return api_service[: -len("/api")]
        else:
            printer.safe_print(f"Warning: CLI is configured with non-standard URL: {api_service}", file=sys.stderr)
            return api_service
    else:
        return None


class TectonCommand(click.Command):
    # used by integration tests
    skip_config_check = False

    """Base class for Click which implements required_auth and uses_workspace behavior, as well as analytics."""

    def __init__(self, *args, callback, requires_auth=True, uses_workspace=False, **kwargs):
        @functools.wraps(callback)
        @click.pass_context
        def wrapper(ctx, *cbargs, **cbkwargs):
            host = _cluster_url()
            cluster_configured = host is not None

            command_names = []
            cur = ctx
            # The top level context is `cli` which we don't want to include.
            while cur:
                command_names.append(cur.command.name)
                cur = cur.parent
            command_names.reverse()

            # Do not try logging events if cluster has never be configured or if user is trying to log in,
            # otherwise the CLI either won't be able to find the MDS or auth token might have expired
            if cluster_configured:
                if uses_workspace:
                    printer.safe_print(f'Using workspace "{common.get_current_workspace()}" on cluster {host}')
                start_time = pendulum.now("UTC")
                state_update_event = ctx.invoke(callback, *cbargs, **cbkwargs)
                execution_time = pendulum.now("UTC") - start_time
                if requires_auth:
                    if state_update_event:
                        # TODO: Include sub-command?
                        analytics.log_cli_event(command_names[1], execution_time, state_update_event)
                        if state_update_event.error_message:
                            sys.exit(1)
                    else:
                        analytics.log_cli_event(command_names[1], execution_time)
            elif not requires_auth or TectonCommand.skip_config_check:
                # Do not try executing anything besides unauthenticated commnds (`login`, `version`) when cluster hasn't been configured.
                state_update_event = ctx.invoke(callback, *cbargs, **cbkwargs)
            else:
                printer.safe_print(
                    f"`{' '.join(command_names)}` requires authentication. Please authenticate using `tecton login`."
                )
                sys.exit(1)

        super().__init__(*args, callback=wrapper, **kwargs)


class TectonGroup(click.Group):
    """Routes group.command calls to use TectonCommand instead of the base Click command"""

    command_class = TectonCommand


TectonGroup.group_class = TectonGroup


@dataclass
class HiddenValue:
    """Wraps a string and displays it as ****. Used to hide passwords when showing the previous value in prompts."""

    value: str

    def __str__(self):
        return "*" * len(self.value)


class HiddenValueType(click.ParamType):
    name = "TEXT"  # Controls how this is displayed in help text

    def convert(self, value, param=None, ctx=None):
        if value is None:
            return None
        if isinstance(value, HiddenValue):
            return value
        return HiddenValue(value)


def tecton_config_option(
    key: str, param_decls: Optional[List[str]] = None, hide_input: bool = False, **kwargs
) -> Callable:
    """Decorator for a Click option which defaults to a value from tecton_spark.conf and prompts if the key is not set.

    :arg key The tecton_spark.conf key.
    :arg param_decls The Click param_decls.
    :arg hide_input Whether to hide user input in the prompt, as for passwords. Additionally, if a default is set,
         it will be obfuscated with `*` in the prompt.
    """
    if "prompt" not in kwargs:
        kwargs["prompt"] = True
    lower_key = key.lower().replace("_", "-")
    param_decls = param_decls or [f"--{lower_key}"]
    default = lambda: conf.get_or_none(key)
    if hide_input:
        kwargs["type"] = HiddenValueType()
        default = HiddenValueType().convert(conf.get_or_none(key))

    def decorator(f):
        @click.option(*param_decls, **kwargs, hide_input=hide_input, default=default)
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            def unwrap(v):
                return v.value if isinstance(v, HiddenValue) else v

            return f(**{k: unwrap(v) for k, v in kwargs.items()})

        return wrapper

    return decorator
