import sys
import argparse
from pathlib import Path

from scorer_edge.l2dc import __file__ as l2dc_file


def main() -> int:

    PROG_DESCRIPTION='''\
description:
  this package can show the CMake module directory useful for setting ScorerEdgeL2dc_ROOT
  and the CMake prefix directory for CMAKE_PREFIX_PATH.
'''

    PROG_EPILOG='''\
examples:
  python -m scorer-edge-l2dc --cmake-dir
  python -m scorer-edge-l2dc --cmake-prefix

  cmake -S src/ -B build/ -DScorerEdgeL2dc_ROOT=$(python3 -m scorer_edge.l2dc --cmake-dir)
  cmake -DCMAKE_PREFIX_PATH=$(python3 -m scorer_edge.l2dc --cmake-prefix)
'''

    ap = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=PROG_DESCRIPTION,
                                 epilog=PROG_EPILOG)

    apm = ap.add_mutually_exclusive_group()
    apm.add_argument("--cmake-dir",     action='store_true', help="show the CMake module directory")
    apm.add_argument("--cmake-prefix",  action='store_true', help="show the package installation prefix")

    args = ap.parse_args()

    if not sys.argv[1:]:
        ap.print_help()

    else:
        prefix = Path(l2dc_file).parent

        if args.cmake_dir:
            print(prefix / "share/cmake")

        if args.cmake_prefix:
            print(prefix)

    return 0


try:
    sys.exit(main())
except Exception as e:
    sys.exit(f'Error: {e}')


# Ref.
# https://docs.python.org/3/library/__main__.html#main-py-in-python-packages
# https://github.com/scikit-build/scikit-build-sample-projects/blob/master/projects/hello-cmake-package/src/hello/__main__.py.in

# End
