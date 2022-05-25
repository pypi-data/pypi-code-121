from click import echo, progressbar
from colorama import Fore, Style, init

init()


def normal(message: str) -> None:
    echo(f"  {message}")


def success(message: str) -> None:
    echo(
        f"{Fore.GREEN}{Style.BRIGHT} ✓ {message}{Style.RESET_ALL}",
        color=True,
    )


def error(message: str) -> None:
    echo(
        f"{Fore.RED}{Style.BRIGHT} x {message}{Style.RESET_ALL}",
        color=True,
    )


def info(message: str) -> None:
    echo(
        f"{Fore.YELLOW}{Style.NORMAL} • {message}{Style.RESET_ALL}",
        color=True,
    )


def progress(iterable, message, *args, **kwargs):
    return progressbar(
        iterable,
        label=f"{Fore.YELLOW}{Style.NORMAL}{message}{Style.RESET_ALL}",
        color=True,
        bar_template=f"%(label)s "
        f"{Fore.CYAN}{Style.DIM}[%(bar)s]{Style.RESET_ALL} "
        f"{Fore.GREEN}{Style.BRIGHT}%(info)s{Style.RESET_ALL}",
        *args,
        **kwargs,
    )
