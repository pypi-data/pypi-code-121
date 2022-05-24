import asyncio
import sys
import time
from types import TracebackType
from typing import Any, Optional, Tuple, Type

import click
import grpc

from jetpack import cron
from jetpack.cmd import _util
from jetpack.cmd._cron import cron_group
from jetpack.cmd._params import ENTRYPOINT_PARAMS
from jetpack.config import _symbols
from jetpack.config._symbols import Symbol
from jetpack.core._jetpack_function import JetpackFunction
from jetpack.runtime._client import client

_original_excepthook = sys.excepthook


def handle_sys_excepthook(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_traceback: Optional[TracebackType],
) -> Any:
    """
    This function handles the empty sys.excepthook error.
    One possible explanation is that module members are set to `None` during module cleanup.
    At the time when `sys.excepthook` is called, all module members are already set to `None`.
    And since python doesn't guarantee the order of modules being cleaned up,
    modules accessing a cleaned up module will result in an uncaught exception of empty.
    This function re-invokes the original sys.excepthook upon such error.
    """
    _original_excepthook(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_sys_excepthook


_using_new_cli = False


def is_using_new_cli() -> bool:
    """
    for legacy uses, we keep old cli. This function disables that logic to ensure
    we don't run the cli command twice.
    """
    return _using_new_cli


@click.group()
def cli() -> None:
    global _using_new_cli
    _using_new_cli = True


@click.command(help="Executes jetpack task")
@click.option("--entrypoint", **ENTRYPOINT_PARAMS)
@click.option("--exec-id", required=True)
@click.option("--qualified-symbol", required=True)
@click.option("--encoded-args", default=None)
def exec_task(
    entrypoint: str,
    exec_id: str,
    qualified_symbol: str,
    encoded_args: str,  # jsonpickle encoded string
) -> None:
    _util.load_user_entrypoint(entrypoint)
    func = _symbols.get_symbol_table().get_registered_symbols()[
        Symbol(qualified_symbol)
    ]

    async def _exec_task() -> Tuple[Optional[Any], Optional[Exception]]:
        args = b""
        if encoded_args:
            args = encoded_args.encode()
        else:
            response = await client.get_task(exec_id)
            args = response.encoded_args

        return await JetpackFunction(func).exec(exec_id, args)

    asyncio.run(_exec_task())


@click.command(help="Executes a cronjob or jetroutine")
@click.option("--entrypoint", **ENTRYPOINT_PARAMS)
@click.option("--qualified-symbol", required=True)
@click.option("--match-suffix", is_flag=True, default=False)
def exec_cronjob(entrypoint: str, qualified_symbol: str, match_suffix: bool) -> None:
    _util.load_user_entrypoint(entrypoint)
    symbols_table = _symbols.get_symbol_table()

    if match_suffix:
        func = symbols_table.get_registered_symbols().get(Symbol(qualified_symbol))
        if func is None:
            # Try fuzzy matching.
            all_symbols = symbols_table.defined_symbols()
            matching_funcs = [x for x in all_symbols if x.endswith(qualified_symbol)]
            num_funcs = len(matching_funcs)

            if num_funcs == 1:
                func = symbols_table.get_registered_symbols()[matching_funcs[0]]
            else:
                if not num_funcs:
                    print(
                        f"Unable to find function {qualified_symbol} in your project."
                    )
                else:
                    print(
                        f"Found multiple functions with name {qualified_symbol} in your project."
                    )
                    print(
                        "Did you mean any of the following:\n\t"
                        + "\n\t".join(matching_funcs)
                    )
                return
    else:
        # Fail and throw error if key is not found in table.
        func = symbols_table.get_registered_symbols()[Symbol(qualified_symbol)]
    asyncio.run(JetpackFunction(func).exec(post_result=False))


@click.command(help="Registers jetpack functions with runtime")
@click.option("--entrypoint", **ENTRYPOINT_PARAMS)
def register(entrypoint: str) -> None:
    async def _register() -> None:
        _util.load_user_entrypoint(entrypoint)
        await client.register_app(cron.get_jobs())

    asyncio.run(_register())


@click.command(help="De-registers jetpack functions with runtime")
def deregister() -> None:
    async def _deregister() -> None:
        await client.deregister_app()

    asyncio.run(_deregister())


@click.command(help="List jetroutines")
@click.option("--entrypoint", **ENTRYPOINT_PARAMS)
def ls(entrypoint: str) -> None:
    _util.load_user_entrypoint(entrypoint)
    # print each symbol on its own line
    print("\n".join(_symbols.get_symbol_table().defined_symbols()))


cli.add_command(exec_task)
cli.add_command(exec_cronjob)
cli.add_command(register)
cli.add_command(deregister)
cli.add_command(ls)
cli.add_command(cron_group)
