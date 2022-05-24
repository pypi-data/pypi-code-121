"""
PSCAD Automation Library
"""

import mhi.common, mhi.pscad

from argparse import ArgumentParser, Namespace
from mhi.common.zipper import LibraryZipper
from mhi.pscad.buildtime import BUILD_TIME


def version(args: Namespace):
    print("MHI PSCAD Library v{} ({})".format(mhi.pscad.VERSION, BUILD_TIME))
    print("(c) Manitoba Hydro International Ltd.")
    print()
    print(mhi.common.version_msg())

def main():
    parser = ArgumentParser(prog='py -m mhi.pscad')
    parser.set_defaults(func=version)
    subparsers = parser.add_subparsers()

    updater = LibraryZipper('PSCAD', 'mhi.pscad', 'mhi.common')
    updater.add_subparser(subparsers)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
