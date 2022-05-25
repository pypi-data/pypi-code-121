import sys
from typing import Any, Callable, List, Optional

import click
import sentry_sdk

import vessl
from vessl.util import logger
from vessl.util.constant import VESSL_LOG_LEVEL
from vessl.util.exception import (
    DEFAULT_ERROR_MESSAGE,
    InvalidTokenError,
    VesslException,
)


def no_interaction_callback(ctx: click.Context, param: click.Parameter, value: bool):
    ctx.obj["no_interaction"] = value


no_interaction_option = click.Option(
    ["--no-interaction"],
    is_flag=True,
    is_eager=True,
    expose_value=False,
    hidden=True,
    callback=no_interaction_callback,
)


class VesslArgument(click.Argument):
    """Custom argument class"""

    def __init__(self, *args, **kwargs) -> None:
        self.prompter = kwargs.pop("prompter", None)
        super().__init__(*args, **kwargs)

    def process_value(self, ctx: click.Context, value: Any) -> Any:
        """Override parent method to invoke prompter before processing value."""
        if (
            (value is None or (self.multiple == True and not value))
            and self.prompter is not None
            and not ctx.obj["no_interaction"]
        ):
            value = self.prompter(ctx, self, value)

        return super().process_value(ctx, value)


class VesslOption(click.Option):
    """Custom option class"""

    def __init__(self, *args, **kwargs) -> None:
        self.prompter = kwargs.pop("prompter", None)
        super().__init__(*args, **kwargs)

    def process_value(self, ctx: click.Context, value: Any) -> Any:
        """Override parent method to invoke prompter before processing value."""
        if (
            (value is None or (self.multiple == True and not value))
            and self.prompter is not None
            and not ctx.obj["no_interaction"]
        ):
            value = self.prompter(ctx, self, value)

        return super().process_value(ctx, value)


class VesslCommand(click.Command):
    def __init__(
        self,
        login_required: bool = False,
        params: Optional[List[click.Parameter]] = None,
        **kwargs,
    ) -> None:
        self.login_required = login_required

        params = params or []
        params = [no_interaction_option] + params

        super().__init__(params=params, **kwargs)

    def make_context(self, *args, **kwargs) -> click.Context:
        if self.login_required:
            vessl.vessl_api.set_access_token(no_prompt=True)

        return super().make_context(*args, **kwargs)


class VesslGroup(click.Group):
    command_class = VesslCommand

    def vessl_command(self, login_required: bool = True, *args, **kwargs):
        kwargs["login_required"] = login_required
        return super().command(*args, **kwargs)

    def main(self, *args, **kwargs):
        try:
            return super().main(*args, **kwargs)

        except InvalidTokenError:
            print("Invalid access token. Please run `vessl configure`.")
            return

        except VesslException as e:
            exc_info = e if VESSL_LOG_LEVEL == "DEBUG" else False
            logger.exception(f"{e.__class__.__name__}: {str(e)}", exc_info=exc_info)
            sys.exit(e.exit_code)

        except Exception as e:
            sentry_sdk.capture_exception(e)
            sentry_sdk.flush()

            exc_info = e if VESSL_LOG_LEVEL == "DEBUG" else False
            logger.fatal(DEFAULT_ERROR_MESSAGE, exc_info=exc_info)
            sys.exit(1)


def vessl_argument(*param_decls: str, **attrs: Any) -> Callable:
    attrs["cls"] = VesslArgument
    return click.argument(*param_decls, **attrs)


def vessl_option(*param_decls: str, **attrs: Any) -> Callable:
    attrs["cls"] = VesslOption
    return click.option(*param_decls, **attrs)
