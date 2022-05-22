#!/usr/bin/env python3

import argparse
import sqlite3
import sys
from getpass import getuser
from pathlib import Path
from traceback import print_tb

from grantme.constants.misc import PROG
from grantme.constants.msgs import DURATION_HELP, INIT_HELP, PROG_HELP, USER_HELP
from grantme.procedures import (
    grant_and_print_result,
    print_status,
    revoke_and_print_result,
)
from grantme.utils.errors import UNEXPECTED_ERROR_CODE, GrantmeError
from grantme.utils.printers import error
from grantme.utils.setup import create_db, create_motd


DB_FILENAME = "db.sqlite3"
DATA_DIR = Path("/var/lib/grantme")
DB_FILE = DATA_DIR / DB_FILENAME


def main():
    current_user = getuser()

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(PROG_HELP),
    )
    parser.add_argument("-s", "--status", action="store_true")
    parser.add_argument("-m", "--mode", choices=["exclusive", "shared"])
    parser.add_argument("-d", "--duration", default="30m", help=DURATION_HELP)
    parser.add_argument("-r", "--revoke", action="store_true")
    parser.add_argument("-u", "--user", default=current_user, help=USER_HELP)
    parser.add_argument("-i", "--init", action="store_true", help=INIT_HELP)

    args = parser.parse_args()

    if args.init:
        try:
            create_db(DATA_DIR, DB_FILE)
        except Exception as err:
            error(
                "Failed to initiate the database. Please ensure that you have root"
                f" privilege for creating {DB_FILE} file. To resolve corrupted"
                f" database files, you may remove {DB_FILE} and then run"
                f" `{PROG} --init` to create a new one."
            )
            error(f"Original exception: {err}")
            sys.exit(UNEXPECTED_ERROR_CODE)

        create_motd()

    try:
        exit_code = 0

        conn = sqlite3.connect(str(DB_FILE), detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row

        if args.init:
            pass  # to prevent printing CLI help message... should fix parser later!
        elif args.status:
            print_status(current_user, conn)
        elif args.revoke:
            revoke_and_print_result(args.user, conn)
        elif args.mode is not None:
            assert args.mode in ("shared", "exclusive")
            grant_and_print_result(
                current_user, args.mode == "shared", args.duration, conn
            )
        else:
            parser.print_help()
    except GrantmeError as err:
        error(err.msg)
        exit_code = err.code
    except Exception as err:
        error(f"Unexpected exception: {err}")
        print_tb(err.__traceback__)
        exit_code = UNEXPECTED_ERROR_CODE
    finally:
        conn.close()
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
