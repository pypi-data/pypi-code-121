"""Prep __main__.py."""
# pylint: disable=invalid-name
import logging
from pathlib import Path
from typing import List, Optional

import typer
from rich.logging import RichHandler
from set_loglevel import set_loglevel

from json_de2zh import __version__, json_de2zh

logging.basicConfig(
    handlers=[RichHandler()],
    format="%(message)s",
    datefmt="%y%m%d %H:%M:%S",
)
_ = ".".join(Path(__file__).with_suffix("").parts[-2:])
logger = logging.getLogger(_)
logger.setLevel(set_loglevel())

# logger.info("__name__: %s", __name__)
# logger.info("__file__: %s", __file__)
logger.debug("logger for this file: %s", _)
# logger.info("logger for this file: %s ", _)
logger.info("set_loglevel(): %s ", set_loglevel())


app = typer.Typer(
    name="json-de2zh",
    add_completion=False,
    help="json-de2zh help",
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{app.info.name} v.{__version__} -- ...")
        raise typer.Exit()


@app.command()
def main(
    words: Optional[List[str]] = typer.Argument(
        None,
        metavar="word1 [word2]...",
        help="files (absolute or relative paths) to be aligned; if only one file is specified, the -s flag must be used to signal it's an english/chinese mixed text file and needs to be separated.",
    ),
    version: Optional[bool] = typer.Option(  # pylint: disable=(unused-argument
        None,
        "--version",
        "-v",
        "-V",
        help="Show version info and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
):
    """Look up words from json/mdx_dict."""
    logger.debug("collecting inputs")
    logger.debug("words: %s", words)
    if words is None:
        words = []
    for word in words:
        print(word, json_de2zh(word))


if __name__ == "__main__":
    app()
