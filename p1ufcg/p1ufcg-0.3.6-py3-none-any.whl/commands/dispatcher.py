from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import logging
from subprocess import check_call, CalledProcessError

import p1
from p1.colors import *
from p1.utils import cprint

config = p1.get_config()
log = logging.getLogger('dispatcher')
handler_file = logging.FileHandler(os.path.expanduser('~/.p1/logs'))
handler_file.setFormatter(logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s'))
log.addHandler(handler_file)
log.setLevel(logging.DEBUG)

EXTERNALS = [
    "status",
    "new",
    "delete",
]

def run_external_command(command, args):
    script_name = os.path.expanduser("p1-%s" % command)
    args.insert(0, script_name)
    try:
        exit = check_call(args)
    except CalledProcessError as e:
        sys.exit(e.returncode)
        pass
    except OSError:
        print("p1: comando não encontrado: '%s'" % command, file=sys.stderr)


def identify_and_run_command(args):
    from distutils.spawn import find_executable
    if args and (args[0] in EXTERNALS):
        command_name = args.pop(0)
        run_external_command(command_name, args)

    elif args and find_executable('p1-%s' % args[0]):
        command_name = args.pop(0)
        run_external_command(command_name, args)

    else: 
        command_name = "help"
        import p1.commands.help as help
        help.main()

    return command_name


def dispatcher(args):
    possible_command = args[0] if args else None
    if possible_command in ['--version', '-v', 'version']:
        import p1.commands.version as version
        version.main()

    elif possible_command == 'info':
        import p1.commands.info as info
        info.main()

    elif possible_command == 'login':
        import p1.commands.login as login
        login.main()

    elif possible_command == 'logout':
        import p1.commands.logout as logout
        logout.main()

    elif possible_command == 'ls':
        import p1.commands.ls as ls
        ls.main()

    elif possible_command == 'commit':
        dirtype = p1.dirtype()
        if dirtype == "old:activity":
            cprint(LRED, "┌──────────────────────────────────────────────────────────┐")
            cprint(LRED, "│ Oops...                                                  │")
            cprint(LRED, "│                                                          │")
            cprint(LRED, "│ This directory contains an activity in an old format. It │")
            cprint(LRED, "│ is no longer supported, however. Consider discarding     │")
            cprint(LRED, "│ this directory and performing a new checkout of the same │")
            cprint(LRED, "│ activity from the source site to have it updated to the  │")
            cprint(LRED, "│ latest version and current format.                       │")
            cprint(LRED, "└──────────────────────────────────────────────────────────┘")
            sys.exit(1)

        elif dirtype in ["assignment", None]:
            import p1.commands.commit as commit
            commit.main()

        else:
            cprint(LRED, "Nenhuma atividade foi encontrada neste diretório")
            sys.exit(1)

    elif possible_command == 'checkout':
        dirtype = p1.dirtype()
        if dirtype == "old:activity":
            cprint(YELLOW, "┌─────────────────────────────────────────────────────────┐")
            cprint(YELLOW, "│ IMPORTANT                                               │")
            cprint(YELLOW, "│                                                         │")
            cprint(YELLOW, "│ This is an old style activity. The old checkout command │")
            cprint(YELLOW, "│ will be used.                                           │")
            cprint(YELLOW, "└─────────────────────────────────────────────────────────┘")
            run_external_command("checkout", args[1:])

        elif dirtype not in [None, "assignment"]:
            cprint(LRED, "┌───────────────────────────────────────────────┐")
            cprint(LRED, "│ checkout cannot be executed in this directory │")
            cprint(LRED, "│                                               │")
            cprint(LRED, "│ Currently, the checkout command must be used  │")
            cprint(LRED, "│ in a non p1 directory.                        │")
            cprint(LRED, "└───────────────────────────────────────────────┘")

        else:
            import p1.commands.checkout as checkout
            checkout.main()

    elif possible_command == 'update':
        cprint(LRED, "┌─────────────────────────────────────┐")
        cprint(LRED, "│ update is deprecated                │")
        cprint(LRED, "│                                     │")
        cprint(LRED, "│ Use pip to update p1:               │")
        cprint(LRED, "│ $ pip install p1 --upgrade --user   │")
        cprint(LRED, "└─────────────────────────────────────┘")

    elif possible_command == 'config':
        cprint(LRED, "┌────────────────────────────────────────────────────┐")
        cprint(LRED, "│ config is deprecated                               │")
        cprint(LRED, "│                                                    │")
        cprint(LRED, "│ Edit ~/.p1/config.yaml directly to configure p1.   │")
        cprint(LRED, "│ See documentation to see existing options.         │")
        cprint(LRED, "└────────────────────────────────────────────────────┘")

    else:
        command = identify_and_run_command(args)


def main():
    if os.name != "posix":
        osplatform = f"{os.name}/{sys.platform}"
        print("┌────────────────────────────────────────────────────┐")
        print("│ Ops... sorry,                                      │")
        print("│ p1 was designed to run on unix like sysyems        │")
        print("│ (unix, linux, macos, etc.)                         │")
        print("│                                                    │")
        print(f"│ It seems your system is: {osplatform:26.26}│")
        print("└────────────────────────────────────────────────────┘")
        sys.exit(1)

    try:
        args = sys.argv[:]
        args.pop(0) # pop dispatcher name
        dispatcher(args)
    except AssertionError as e:
        cprint(LRED, e)

    except KeyboardInterrupt:
        cprint(LRED, "\nUser interruption")
