"""
AIML Interpreter CLI
====================

Command line interface to work with pyaiml21 - AIML 2.1 compatible
interpreter. The running program represents a single chatbot
that can chat with multiple users (see options).

The structure of the bot, or the file extensions are as follows:

    * to load the bot, pass in the bot directory with all files
    * .aiml files should be stored in /aiml/*.aiml, or /*.aiml
    * .aimlif in /aimlif/*.aimlif or /aimlif/*.csv or /*.aimlif
    * maps in /maps/* or /*.map
    * sets in /sets/* or /*.set
    * properties in `/properties.*` or in /config/propert*
    * substitutions in /*.substitution* or /substitutions/* or config/*.substitution*

The order of loading the files is the same as above.
"""
import argparse
from pyaiml21 import Bot
from pyaiml21.utils import load_aiml_set, load_aiml_sub, load_aiml_map
from glob import glob
from pathlib import Path
import signal
import sys


###############################################################################
#  P a r s e r
###############################################################################


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawTextHelpFormatter)
    action = parser.add_mutually_exclusive_group(required=False)

    action.add_argument("-i", "--interactive",
                        default=True,
                        action="store_true",
                        help="(load files and) start interactive session"
                        )

    action.add_argument("-d", "--debug",
                        default=False,
                        action="store_true",
                        help="(load files and) start debugging session"
                        )

    action.add_argument("--validate",
                        default=False,
                        action="store_true",
                        help="just validate the files and return"
                        )

    # parser.add_argument("-l", "--load", type=str,
    #                     help="Load compiled file"
    # )

    parser.add_argument("--bot", type=str, nargs="?", metavar="folder",
                        help="load bot from folder")
    parser.add_argument("--aiml", type=str, nargs="*", metavar="file",
                        help="paths to .aiml files")
    parser.add_argument("--aimlif", type=str, nargs="*", metavar="file",
                        help="paths to .aimlif files")
    parser.add_argument("--substitutions", type=str, nargs="*", metavar="file",
                        help="paths to substitutions to load, the concrete "
                             "type will be decided based on the file name")
    parser.add_argument("--properties", type=str, nargs="*", metavar="file",
                        help="paths to bot properties")
    parser.add_argument("--maps", type=str, nargs="*", metavar="file",
                        help="paths to AIML maps, map name will be decided "
                             "based on the file name (name.txt, name.map)")
    parser.add_argument("--sets", type=str, nargs="*", metavar="file",
                        help="paths to AIML sets, set name will be decided "
                             "based on the file name (name.txt, name.set)")
    parser.add_argument("-v", "--verbose", default=False,
                        action="store_true", help="enable debugging info")
    parser.add_argument("--multiuser", default=False, action="store_true",
                        help="applicable only for interactive mode, when set "
                             "each input contains as a first word the user "
                             "id")

    return parser


###############################################################################
#  F u n c t i o n s   t o   l o a d   d a t a
###############################################################################


def load_aiml(bot: Bot, paths: list, verbose=False):
    for p in paths:
        for file in glob(p):
            if verbose:
                print("[info] Loading .aiml file ..", file)
            try:
                logger = bot.learn_aiml(file)
                if logger.has_errors() or logger.has_warnings():
                    print(logger.report())
                if logger.has_errors():
                    print("[info] Failed to load ..", file)
                elif verbose:
                    print("[info] OK", file)
            except Exception as e:
                print("[info] Could not load AIML file", file, e)
    return bot


def load_aimlif(bot: Bot, paths: list, verbose=False):
    for p in paths:
        for file in glob(p):
            if verbose:
                print("[info] Loading .aimlif file ..", file)
            try:
                logger = bot.learn_aimlif(file)
                if logger.has_errors() or logger.has_warnings():
                    print(logger.report())
                if logger.has_errors():
                    print("[info] Failed to load ..", file)
                elif verbose:
                    print("[info] OK", file)
            except Exception as e:
                print("[info] Could not load AIMLIF file", file, e)
    return bot


def load_sets(bot: Bot, paths: list, verbose=False):
    for p in paths:
        for file in glob(p):
            set_name = Path(file).stem
            if verbose:
                print("[info] Loading AIML set..", file, "as", set_name)
            try:
                the_set = load_aiml_set(file)
                bot.load_set(set_name, the_set)
                if verbose:
                    print("[info] OK", file, "as", set_name)
            except Exception as e:
                print("[info] Could not load AIML set file", file, e)
    return bot


def load_maps(bot: Bot, paths: list, verbose=False):
    for p in paths:
        for file in glob(p):
            name = Path(file).stem
            if verbose:
                print("[info] Loading AIML map..", file, "as", name)
            try:
                the_map = load_aiml_map(file)
                bot.load_map(name, the_map)
                if verbose:
                    print("[info] OK", file, "as", name)
            except Exception as e:
                print("[info] Could not load AIML map file", file, e)
    return bot


AVAILABLE_SUBS = {
    "normalize", "denormalize", "gender", "person", "person2"
}


def load_subs(bot: Bot, paths: list, verbose=False):
    for p in paths:
        for file in glob(p):
            name = Path(file).stem
            if verbose:
                print("[info] Loading substitutions..", file)
            sub_name = None
            for available in AVAILABLE_SUBS:
                if available.startswith(name):
                    sub_name = name
            if sub_name is None:
                print("[error] Could not load..", file)
                continue
            try:
                subs = load_aiml_sub(file)
                bot.add_substitutions(sub_name, subs)
                if verbose:
                    print("[info] OK", file, "as", sub_name)
            except Exception as e:
                print("[info] Could not load substitution file", file, e)
    return bot


def load_props(bot: Bot, paths: list, verbose=False):
    for p in paths:
        for file in glob(p):
            if verbose:
                print("[info] Loading properties..", file)
            try:
                props = load_aiml_map(file)
                bot.add_properties(props)
                if verbose:
                    print("[info] OK", file)
            except Exception as e:
                print("[info] Could not load properties file", file, e)
    return bot


def load_bot(bot: Bot, path: str, verbose=False):
    p = Path(path)
    load_aiml(bot, glob(str(p / "*.aiml")), verbose)
    load_aiml(bot, glob(str(p / "aiml" / "*.aiml")), verbose)

    load_aimlif(bot, glob(str(p / "*.aimlif")), verbose)
    load_aimlif(bot, glob(str(p / "aimlif" / "*.aimlif")), verbose)
    load_aimlif(bot, glob(str(p / "aimlif" / "*.csv")), verbose)

    load_sets(bot, glob(str(p / "*.set")), verbose)
    load_sets(bot, glob(str(p / "sets" / "*")), verbose)

    load_maps(bot, glob(str(p / "*.map")), verbose)
    load_maps(bot, glob(str(p / "maps" / "*")), verbose)

    load_subs(bot, glob(str(p / "substitutions" / "*")), verbose)
    load_subs(bot, glob(str(p / "*.substitution*")), verbose)
    load_subs(bot, glob(str(p / "config" / "*.substitution*")), verbose)

    load_props(bot, glob(str(p / "properties.*")), verbose)
    load_props(bot, glob(str(p / "config" / "propert*")), verbose)


###############################################################################
#  M a i n s
###############################################################################


# catch ctrl-c
def signal_handler(_sig, _frame):
    print()
    print("[exiting..]")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

USER_ID = "1"


def main():
    parser = create_parser()
    args = parser.parse_args()
    bot = Bot()
    verbose = args.verbose
    have_data = False

    # first try to load any data from command line
    all_args = [args.bot, args.aiml, args.aimlif, args.maps, args.sets,
                args.properties, args.substitutions]
    all_func = [load_bot, load_aiml, load_aimlif, load_maps, load_sets,
                load_props, load_subs]

    for a, f in zip(all_args, all_func):
        if a:
            have_data = True
            f(bot, a, verbose)

    # if only validation, return
    if args.validate:
        return

    # if we have no data, print help and exit
    if not have_data:
        parser.print_help()
        parser.exit(status=1,
                    message="\nExpected some data paths, found none\n")

    # otherwise run the main loop...
    try:

        multi: bool = args.multiuser
        # print the info message
        if args.debug:
            # not supported for debugging
            multi = False
            print("Starting debugging session, use ^C to exit...")
            print()
        else:
            print("Starting interactive session, use ^C to exit...")
            print()

        while True:
            input_ = input(">>> ")
            if multi:
                user_id, input_ = input_.split(None, maxsplit=1)
            else:
                user_id = USER_ID
            response = bot.respond(input_,user_id, args.debug)
            print(response.replace("<br></br>", "\n"))

    except Exception as e:
        if verbose:
            print("[end]", e)


if __name__ == "__main__":
    main()
