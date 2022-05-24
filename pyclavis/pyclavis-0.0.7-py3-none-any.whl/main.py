import sys
import os
import json

import getpass

from .logging import log, print_t, print_e, setdebug

from .gui import (
    VERSION,
    readkeyfile,
    startup,
    ask_startup_passphrase,
    check_instance_or_die,
    CredentialStore,
)
from .common import createkeystorage, readkeystore
from .favorites import load_favorites, save_favorites


def startgui():

    setdebug()

    # keep rc, otherwise socket gets closed by garbage collection
    rc = check_instance_or_die()

    ask_startup_passphrase()

    startup()


def readpassphrase():
    clavis = readkeyfile()
    if clavis == None:
        while True:
            clavis = getpass.getpass("enter password: ").strip()
            if len(clavis) > 0:
                break
    return clavis


def cmdline():

    import argparse

    parser = argparse.ArgumentParser(
        prog="pyclavis",
        usage="python3 -m %(prog)s [options]",
        description="pyclavis password manager",
        epilog="for more information refer to https://github.com/kr-g/pyclavis",
    )
    parser.add_argument(
        "-v",
        "--version",
        dest="show_version",
        action="store_true",
        help="show version info and exit",
        default=False,
    )
    parser.add_argument(
        "-V",
        "--verbose",
        dest="show_verbose",
        action="store_true",
        help="show more info",
        default=False,
    )

    exportgroup = parser.add_mutually_exclusive_group()

    exportgroup.add_argument(
        "--export",
        dest="do_export",
        action="store_true",
        help="export key-store to stdout as csv",
        default=False,
    )
    exportgroup.add_argument(
        "--export-json",
        dest="do_export_json",
        action="store_true",
        help="export key-store to stdout as json",
        default=False,
    )
    exportgroup.add_argument(
        "--export-favorites",
        dest="do_export_favs",
        action="store_true",
        help="export favorites to stdout as json",
        default=False,
    )

    args = parser.parse_args()
    # print( args )

    if args.show_version:
        print("Version:", VERSION)
        return

    if args.show_verbose:
        setdebug()

    if args.do_export or args.do_export_json:
        passphrase = readpassphrase()
        storage = createkeystorage(passphrase)
        secman = CredentialStore()
        loaded = readkeystore(secman, storage)
        if loaded == None:
            print("wrong password")
            sys.exit(1)

        if args.do_export:
            credits = map(
                lambda x: (x.category if x.category else "", x.name, x.user, x.passwd),
                secman.tolist(),
            )
            for crd in credits:
                print("\t".join([*crd]))

        if args.do_export_json:
            credits = secman.tolist()
            for crd in credits:
                s = json.dumps(crd.__dict__)
                print(s)

        return

    if args.do_export_favs:
        passphrase = readpassphrase()
        favs = load_favorites(passphrase)
        for fa in favs.values():
            s = json.dumps(fa.__dict__)
            print(s)

        return

    return "start"


def main_func():

    rc = cmdline()

    if rc == "start":
        rc = startgui()

    return rc
