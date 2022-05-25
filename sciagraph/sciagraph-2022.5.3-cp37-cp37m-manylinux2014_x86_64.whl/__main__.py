"""
Command-line interface.
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter, REMAINDER
from importlib.util import find_spec
import ctypes
from typing import Tuple
import sys
import os
from datetime import datetime, timezone

from . import __version__


def glibc_version() -> Tuple[int, int]:
    """Get the version of glibc."""
    libc = ctypes.CDLL("libc.so.6")
    get_libc_version = libc.gnu_get_libc_version
    get_libc_version.restype = ctypes.c_char_p
    return tuple(map(int, get_libc_version().split(b".")[:2]))  # type: ignore


_LICENSES_PATH = os.path.join(os.path.dirname(__file__), "licenses.html")
# Make sure we're compliant with open source library licenses, which all need
# to be included:
assert os.path.exists(_LICENSES_PATH)

HELP = f"""\
If you have a program that you usually run like this:

  $ python yourprogram.py --the-arg=x

You can run it like this:

  $ python -m sciagraph run yourprogram.py --the-arg=x

If you have a program that you usually run like this:

  $ python -m yourpackage --your-arg=2

Then you can run it like this:

  $ python -m sciagraph run -m yourpackage --your-arg=2

More documentation is available at https://sciagraph.com/docs/

Third-party open source licenses can be found in {_LICENSES_PATH}
"""

PARSER = ArgumentParser(
    usage="sciagraph [-o output-path] run [-m module | /path/to/script.py ] [arg] ...",
    epilog=HELP,
    formatter_class=RawDescriptionHelpFormatter,
    allow_abbrev=False,
)
PARSER.add_argument("--version", action="version", version=__version__)
PARSER.add_argument(
    "--debug",
    action="store_true",
    default=False,
    help="Run in debug mode, for help with catching bugs in Sciagraph",
)
PARSER.add_argument(
    "-o",
    "--output-path",
    dest="output_path",
    action="store",
    default=os.environ.get(
        "SCIAGRAPH_OUTPUT_PATH",
        "sciagraph-result/"
        + datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
        .replace(":", "-"),
    ),
    help="Directory where the profiling results will be written",
)
PARSER.add_argument(
    "--job-id",
    dest="job_id",
    action="store",
    default=None,
    help="Unique identifier for this job",
)
subparsers = PARSER.add_subparsers(help="sub-command help")
parser_run = subparsers.add_parser(
    "run",
    help="Run a Python script or package",
    prefix_chars=[""],
    add_help=False,
)
parser_run.set_defaults(command="run")
parser_run.add_argument("rest", nargs=REMAINDER)
del subparsers, parser_run

# Can't figure out if this is a standard path _everywhere_, but it definitely
# exists on Ubuntu 18.04 and 20.04, Debian Buster, CentOS 8, and Arch.
# TODO it will be different on Arm
LD_LINUX = "/lib64/ld-linux-x86-64.so.2"


def main():
    if len(sys.argv) == 1:
        PARSER.print_help()
        sys.exit(0)

    args = PARSER.parse_args()
    environ = os.environ.copy()

    # Pass in output path; see get_output_path() in api.rs.
    environ["SCIAGRAPH_OUTPUT_PATH"] = args.output_path

    if args.job_id is not None:
        environ["SCIAGRAPH_JOB_ID"] = args.job_id

    environ["__SCIAGRAPH_INITIALIZE"] = "process"

    # TODO deal with spaces/colons in path.
    if args.debug or os.getenv("SCIAGRAPH_DEBUG") == "1":
        module = "sciagraph._sciagraph_debug"
    else:
        module = "sciagraph._sciagraph"
    to_preload = find_spec(module).origin

    if glibc_version() < (2, 27):
        raise SystemExit(
            "Your version of Linux is too old. See"
            "https://sciagraph.com/docs/reference/supported-platforms"
            " for a list of supported platforms; if you need support for "
            "additional platforms, please email support@sciagraph.com."
        )
    elif glibc_version() >= (2, 30) and os.path.exists(LD_LINUX):
        # Launch with ld.so, which is more robust than relying on
        # environment variables.
        executable = LD_LINUX
        args = ["--preload", to_preload, sys.executable] + args.rest
    else:
        # Fall back to LD_PRELOAD env variable on older versions of glibc.
        executable = sys.executable
        args = args.rest
        environ["LD_PRELOAD"] = to_preload

    os.execve(executable, [executable] + args, env=environ)


if __name__ == "__main__":
    main()
