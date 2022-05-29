"""Prep __main__ entry."""
# pylint: disable=invalid-name, too-many-locals, too-many-arguments, too-many-branches, too-many-statements, duplicate-code
from pathlib import Path
from textwrap import dedent
from typing import List, Optional

# import environs
import logzero
import typer
from icecream import ic, install as ic_install
from logzero import logger

from ezbee import __version__, ezbee, loglevel

# from ezbee.cmat2html import cmat2html
from ezbee.loadtext import loadtext
from ezbee.text2lists import text2lists
from ezbee.gen_pairs import gen_pairs
from ezbee.save_xlsx_tsv_csv import save_xlsx_tsv_csv

# logzero.loglevel(_)
logzero.loglevel(loglevel())


# logger.info(" loglevel: %s", _ or 20)

# logger.debug(" debug: %s", __file__)
# logger.info(" info: %s", __file__)

ic_install()
ic.configureOutput(
    includeContext=True,
    # outputFunction=logger.info,
    outputFunction=logger.debug,
)
ic.enable()

app = typer.Typer(
    name="ezbee",
    add_completion=False,
    help="en-zh-bee aligner",
)

esp_min_samples_expl = dedent(
    """
    Larger esp or smaller min_samples will result in more aligned pairs but also more false positives (pairs falsely identified as candidates). On the other hand, smaller esp or larger min_samples values tend to miss `good` pairs."""
).strip()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(
            f"{app.info.name} v.{__version__} -- visit https://bumblebee.freeforums.net/thread/2/ezbee-cli-related to chat about {app.info.name}."
        )
        raise typer.Exit()


@app.command()
def main(
    files: List[str] = typer.Argument(
        ...,
        metavar="file1 [file2]...",
        help="files (absolute or relative paths) to be aligned; if only one file is specified, the -s flag must be used to signal it's an english/chinese mixed text file and needs to be separated.",
    ),
    eps: float = typer.Option(10, help="epsilon"),
    min_samples: int = typer.Option(
        6, help="eps, min-samples: " + esp_min_samples_expl
    ),
    need_sep: bool = typer.Option(
        False,
        "--need-sep",
        "-s",
        is_flag=True,
        help="Separate input files that are mixed english and chinese text.",
    ),
    show_plot: bool = typer.Option(
        False,
        "--show-plot",
        "-p",
        is_flag=True,
        help="Show heatmap and align trace plots in the default browser.",
    ),
    save_xlsx: bool = typer.Option(
        True,
        help="Save xlsx.",
    ),
    save_tsv: bool = typer.Option(
        True,
        help="Save tsv.",
    ),
    save_csv: bool = typer.Option(
        False,
        help="Save csv.",
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
    """Align en-zh texts.

    e.g.

    * ezbee file1 file2

    * ezbee file1 file2 -p  # show plots

    * ezbee file1 -s

    * ezbee file1 file2 -s
    """
    logger.info("Collecting inputs...")
    # test show-plot -p
    # logger.info(show_plot)
    logger.debug("show-plot: %s", show_plot)

    logger.debug("files: %s", files)

    if not show_plot and not save_xlsx and not save_tsv and not save_csv:
        exiting = typer.style("exiting...", fg=typer.colors.RED, bold=True)
        typer.echo(
            "None of show-plot, save-xlsx, save-tsv and save-csv is set to True: nothing to do, "
            f"{exiting}"
        )
        raise typer.Exit(code=0)

    if not files:
        typer.echo("Provide at least one file")
        raise typer.Exit()

    if len(files) == 1 and not need_sep:
        typer.echo(
            "If you only provide one file, you'll also have to specify -s or --need-sep."
        )
        typer.echo("Try again...")
        raise typer.Exit()

    for file_ in files:
        if not Path(file_).is_file():
            typer.echo(f" [{file_}] is not a file or does not exist.")
            raise typer.Exit()

    # paired, two files and need_sep not set
    if len(files) == 2 and not need_sep:
        try:
            text1 = loadtext(files[0])
        except Exception as e:
            logger.error(e)
            raise
        try:
            text2 = loadtext(files[1])
        except Exception as e:
            logger.error(e)
            raise

        list1 = [elm.strip() for elm in text1.splitlines() if elm.strip()]
        list2 = [elm.strip() for elm in text2.splitlines() if elm.strip()]

        logger.debug("len1: %s, len2: %s", len(list1), len(list2))

    # other cases: 2 files + need_sep not set, 3 or or files
    else:  # assume mixed english/chinese, separate
        list1 = []
        list2 = []
        text = ""
        for file in files:
            text = text + "\n" + loadtext(file)
        list1, list2 = text2lists(text)

    # text1 = Path(files[0]).read_text(encoding="utf8").splitlines()
    # text2 = Path(files[1]).read_text(encoding="utf8").splitlines()

    # logger.debug("list1: %s", list1)
    # logger.debug("list2: %s", list2)

    # typer.echo(list1)
    # typer.echo(list2)
    # raise typer.Exit(1)

    try:
        logger.info("Processing data...")
        aset = ezbee(
            list1,
            list2,
            eps=eps,
            min_samples=min_samples,
        )
        # fastlid changed logger.level is changed to 20
        # turn back to loglevel
        logzero.loglevel(loglevel())
        if aset:
            logger.debug("aset: %s...%s", aset[:3], aset[-3:])
    except Exception as e:
        typer.echo(e)
        raise typer.Exit()

    # process show_plot
    logger.debug("show-plot: %s", show_plot)
    if show_plot:
        try:
            from ezbee.cmat2html import cmat2html  # pylint: disable=import-outside-toplevel
            flag = False
        except ModuleNotFoundError:
            logger.warning(" You need to install extras [plot] in order to use this option, e.g. pip install ezbee[plot]==0.1.0a3, exiting...")

            # raise typer.Exit(1) from exc
            flag = True
        except Exception as exc:
            logger.exception(exc)
            flag = True

        if not flag:
            cmat2html(
                ezbee.cmat,
                aset=ezbee.aset,
                show_plot=show_plot,
            )

    logger.debug("Proceed with saving files...")

    aligned_pairs = gen_pairs(list1, list2, aset)
    if aligned_pairs:
        logger.debug("%s...%s", aligned_pairs[:3], aligned_pairs[-3:])

    _ = [save_xlsx, save_tsv, save_csv]
    file_ext = [v1 for v0, v1 in zip(_, [".xlsx", ".tsv", ".csv"]) if v0]
    logger.debug("[save_xlsx, save_tsv, save_csv]: %s, file_ext: %s", _, file_ext)

    if not file_ext:  # nothing to do
        raise typer.Exit(code=0)
    # file =

    logger.info("Saving %s", file_ext)

    _ = Path(files[0]).with_suffix("").as_posix() + "-ali"
    _ = Path(_)
    save_xlsx_tsv_csv(
        aligned_pairs,
        file_ext=file_ext,
        file=_,
    )

    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()


_ = """
https://medium.com/short-bits/typer-the-command-line-script-framework-you-should-use-de9d07109f54
one of many:

from enum import Enum
class FileExt(Enum):
    csv = ".csv"
    tsv = ".tsv"
    xlsx = ".xlsx"

def __main__(
    ...
    file_exc: FileExt = FileExt.xlsx
    ...
)
    typer.echo(f" file_ext: {file_exc.value}")
"""
