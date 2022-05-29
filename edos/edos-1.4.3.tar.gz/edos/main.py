import logging
import sys

import click

from edos import commands, __version__

LOG = logging.getLogger(__name__)

TRACE = logging.DEBUG - 1
logging.addLevelName(TRACE, "TRACE")


@click.group()
@click.option("--verbose", is_flag=True)
@click.version_option(f"{__version__}", "--version", "-v")
def main(verbose):
    from edos.exceptions import UserReadableException

    # Set verbosity level
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s,%(msecs)03d - %(message)s",
        level=log_level,
        datefmt="%H:%M:%S",
    )

    def exception_handler(type, value, traceback):
        if verbose:
            return old_excepthook(type, value, traceback)

        if isinstance(value, UserReadableException):
            LOG.error(str(value))
        elif hasattr(value, "body"):
            # Kubernetes API exception have the interesting info in .body
            # but we avoid importing Kubernetes API to speed up start (200ms).
            LOG.error(getattr(value, "body", str(value)))
        else:
            return old_excepthook(type, value, traceback)

    old_excepthook = sys.excepthook
    sys.excepthook = exception_handler


commands.register_commands(main)
if __name__ == "__main__":
    main()
