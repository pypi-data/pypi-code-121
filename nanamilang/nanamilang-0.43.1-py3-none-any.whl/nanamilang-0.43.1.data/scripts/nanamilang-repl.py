#!python

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

"""NanamiLang REPL"""

import argparse
import atexit
import os
import readline
import sys
import time

import nanamilang.datatypes
from nanamilang.shortcuts import truncated, aligned
from nanamilang import module, loader
from nanamilang.contrib.window import Window
from nanamilang.builtin import BuiltinFunctions, BuiltinMacros
from nanamilang.bdb import BuiltinMacrosDB, BuiltinFunctionsDB
from nanamilang import __version_string__, __author__, __project_license__

repl_history_file_path = os.path.join(
    os.path.expanduser("~"), ".nanamilang_history")
try:
    readline.set_history_length(1000)
    readline.read_history_file(repl_history_file_path)
except FileNotFoundError:
    pass


# Initialize Builtin* DB ...
BuiltinMacrosDB.initialize(BuiltinMacros)
BuiltinFunctionsDB.initialize(BuiltinFunctions)

readline.parse_and_bind("tab: complete")
readline.parse_and_bind('set blink-matching-paren on')

atexit.register(readline.write_history_file, repl_history_file_path)

exit_f_names: list = ['exit!', 'bye!', 'exit', 'bye', 'quit', 'quit!']
available_names = set(BuiltinMacrosDB.names() + BuiltinFunctionsDB.names() + exit_f_names)


def complete(t: str, s: int):
    """NanamiLang REPL, GNU Readline complete callback fn, completes from available names"""
    return ([name for name in available_names if name.startswith(t)] + [None]).__getitem__(s)


readline.set_completer(complete)


def check_whether_user_want_to_exit(m: module.Module) -> None:
    """
    1. m.tokenized() contains only ONE token
    2. that token is a type() of Token.Identifier
    3. that token dt().origin() is something from exit function names

    :param m: REPL module instance which used to evaluate user's inputs
    """

    tip = 'To exit the REPL environment: type ({0}), press a "Control+D"'

    if len(m.tokenized()) == 1:
        first = m.tokenized()[0]
        if first.type() == 'Identifier':
            if first.dt().origin() in exit_f_names:
                print(aligned('', source=tip.format(first.dt().origin()), n=67))


def main():
    """NanamiLang REPL Main function"""

    parser = argparse.ArgumentParser('NanamiLang REPL')
    parser.add_argument('--no-greeting',
                        help='Greeting can be disabled',
                        action='store_true', default=False)
    parser.add_argument('--include-traceback',
                        help='Include exception traceback',
                        action='store_true', default=False)
    parser.add_argument('--show-measurements',
                        help='Show the REPL module stats.',
                        action='store_true', default=False)
    parser.add_argument('--license',
                        help='Show license of NanamiLang',
                        action='store_true', default=False)
    parser.add_argument('--version',
                        help='Show version of NanamiLang',
                        action='store_true', default=False)

    args = parser.parse_args()

    # GNU GPL v2 may require these options

    if args.version:
        print('NanamiLang', __version_string__)
        return 0

    if args.license:
        print('License is', __project_license__)
        return 0

    # Collect Python 3 version into single string
    p_ver = '.'.join([str(sys.version_info.major),
                      str(sys.version_info.minor),
                      str(sys.version_info.micro)])

    # First, good boys always should start with the greeting (it can be disabled)
    print('NanamiLang', __version_string__, 'by', __author__, 'on Python', p_ver)
    if not args.no_greeting:
        print('History path is:', repl_history_file_path)
        if not os.environ.get('NANAMILANG_PATH'):
            print('\nWARN: NANAMILANG_PATH environment variable has not been set\n')
        print()
        print('                         #StandWithUkraine                         ')
        print()
        print('History of computations is stored in *1, *2, and *3 global bindings')
        print('The most recent exception occurred (which we handle) stored in "*e"')
        print()
        print('In order to get documentation of function/macro, follow next steps:')
        print()
        print('  1. Open https://nanamilang.jedi2light.moe in your WebBrowser     ')
        print('  2. Find && press on the "NanamiLang Package Registry" button     ')
        print('  3. Copy && run NanamiLang PKG Manager cURL installation one-liner')
        print('  4. Next, in your Terminal type "nml populate stdlib" command-line')
        print()
        print('Now you can restart NanamiLang REPL environment, and require stdlib')
        print()
        print("  (require 'stdlib)   ;; require NanamiLang Standard Library module")
        print('  (stdlib/doc defn)   ;; for instance, getting doc for "defn" macro')
        print()
        print('Also consider checking other NanamiLang Standard Library functions!')
        print()
        print('If you want to abort __a source code input__, press the "Control-C"')
        print('Type (exit!), (bye!), (exit), (bye), press "Control+D" to exit REPL')

    # Since nanamilang.builtin.BuiltinFunctions provides install() method,
    # we can install functions to help the user to exit NanamiLang REPL in easy way!
    for exit_f_name in exit_f_names:
        BuiltinFunctions.install(
            {
                'name': exit_f_name,
                'forms': [f'({exit_f_name})'],
                'docstring': 'Exit NanamiLang REPL environment with a zero exitcode'
            },
            lambda _: sys.exit(bool(print('Bye for now!')))
        )

    m = module.Module(name='REPL')  # <- initialize NanamiLang Module instance, then

    computations = Window(3)  # <------------- initialize computation history window

    # Update set of the names to autocomplete on 'environment::set' event triggered!
    m.on('environment::set', lambda _: (available_names.add(_[0])))  # <- add to set

    # Initialize REPL globals: *1. *2, *3, *e (like Leiningen REPL)

    e = m.environ()
    e.set('*e', nanamilang.datatypes.Nil('nil'))
    e.set('*1', nanamilang.datatypes.Nil('nil'))
    e.set('*2', nanamilang.datatypes.Nil('nil'))
    e.set('*3', nanamilang.datatypes.Nil('nil'))  # <- initialize as nils by default

    # Initialize NanamiLang Module Loader (and forward '--include-traceback' option)
    loader.Loader.initialize(module.Module,
                             loader.LocalIOLoader, includetb=args.include_traceback)

    while True:
        try:
            try:
                src = input('REPL> ')
            except KeyboardInterrupt:
                print()  # <- a hackish way to force Python to go to newline
                continue
            # Skip the user entered source evaluation in case of empty input
            if not src:
                continue
            # Call m.prepare() to prepare (possibly incomplete) user' source

            m.prepare(src)
            try:
                while m.state().state() != module.Module.ModuleState.StateReady:
                    left_cnt, right_cnt = m.state().meta().get('TBoundariesCnt')
                    src += '\n' + input(f'....> {" " * (left_cnt - right_cnt)}')
                    m.prepare(src)
            except KeyboardInterrupt:
                print()  # <---------------- a hackish way to force Python to go to newline
                continue

            __repl_got_input__ = time.perf_counter()  # remember when we have got the input

            # Show REPL exiting tips in case user wants to exit NanamiLang REPL environment
            check_whether_user_want_to_exit(m)
            # Iterate through results, if encountered NException data type instance, handle
            for dt in m.evaluate().results():
                if isinstance(dt, nanamilang.datatypes.NException):
                    e.set('*e', dt)
                    # Store the most recent NException data type instance to global *e bind
                    if not args.include_traceback:
                        print(truncated(dt.format(src=src), 67))
                    else:
                        print('\n\b',
                              truncated(
                                  dt.format(src=src,
                                            include_traceback=args.include_traceback), 67))
                else:
                    computations.push(dt)  # <- push computation result to computations hst
                    print(truncated(dt.format(), 67))  # <- and print a computation result!
            # Populate computations history ###############################################
            e.set('*1', computations.get(0, default=e.get('*1')))  # <-- store first result
            e.set('*2', computations.get(1, default=e.get('*2')))  # <- store second result
            e.set('*3', computations.get(2, default=e.get('*3')))  # <-- store third result
            ###############################################################################
            # If '--show-measurements' has been passed, show all the available measurements
            if args.show_measurements:
                stats = {'[REPL]': time.perf_counter() - __repl_got_input__}
                # Sadly, we do not count dictionary update operation here as well, it's okay
                stats.update(m.measurements())
                # Also, we don't count: iterating, unpacking, rounding, formatting, printing
                print('\n'.join(
                    [aligned(s, f'{t:.5f} secs.', 67, dots='.') for s, t in stats.items()]))
        except EOFError:
            print("Bye for now!")
            break

    return 0

    # Return 'zero' exit code, and exit NanamiLang REPL after playing around with NanamiLang


if __name__ == "__main__":
    main()
