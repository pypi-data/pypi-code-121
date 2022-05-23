import sys
import logging
from contextlib import contextmanager

from ..orange_version import ORANGE_VERSION

if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
    from oasys.canvas.__main__ import main as orange_main
elif ORANGE_VERSION == ORANGE_VERSION.latest_orange:
    from Orange.canvas.__main__ import main as orange_main
else:
    from orangecanvas.main import Main as OrangeCanvasMain

    class Main(OrangeCanvasMain):
        DefaultConfig = "ewoksorange.canvas.config.Config"

    def orange_main(argv):
        main_instance = Main()
        return main_instance.run(argv)


if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
    import argparse

    def arg_parser():
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--no-discovery",
            action="store_true",
            help="Don't run widget discovery (use full cache instead)",
        )
        parser.add_argument(
            "--force-discovery",
            action="store_true",
            help="Force full widget discovery (invalidate cache)",
        )
        parser.add_argument(
            "--no-welcome", action="store_true", help="Don't show welcome dialog."
        )
        parser.add_argument(
            "--no-splash", action="store_true", help="Don't show splash screen."
        )
        parser.add_argument(
            "--stylesheet",
            help="Application level CSS style sheet to use",
            type=str,
            default=None,
        )
        parser.add_argument(
            "--config",
            help="Configuration namespace",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-l",
            "--log-level",
            help="Logging level (0, 1, 2, 3, 4)",
            type=int,
            default=1,
        )
        return parser

else:
    from orangecanvas.main import arg_parser

from ewoksorange.registration import register_addon_package
from ewoksorange import ewoks_addon


@contextmanager
def temporary_log_handlers(log_level):
    logger = logging.getLogger("ewoksorange")
    logger.setLevel(log_level)
    if logger.hasHandlers():
        yield
    else:
        stdouthandler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stdouthandler)
        yield
        logger.removeHandler(stdouthandler)


def main(argv=None):
    parser = arg_parser()
    parser.add_argument(
        "--with_example",
        action="store_true",
        help="Register example add-on's from ewoksorange.",
    )

    if argv is None:
        argv = sys.argv
    options, _ = parser.parse_known_args(argv[1:])

    if "--with_example" in argv:
        argv.pop(argv.index("--with_example"))

    if "--force-discovery" not in argv:
        argv.append("--force-discovery")

    with temporary_log_handlers(options.log_level):
        register_addon_package(ewoks_addon)

        if options.with_example:
            from ewoksorange.tests.examples import ewoks_example_1_addon
            from ewoksorange.tests.examples import ewoks_example_2_addon

            register_addon_package(ewoks_example_1_addon)
            register_addon_package(ewoks_example_2_addon)

    orange_main(argv)
