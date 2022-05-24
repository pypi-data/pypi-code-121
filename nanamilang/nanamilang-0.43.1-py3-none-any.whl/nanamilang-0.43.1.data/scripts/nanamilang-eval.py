#!python

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

"""NanamiLang Eval"""

import argparse
import os
import sys

from nanamilang.datatypes import Vector
from nanamilang.shortcuts import truncated, aligned
from nanamilang import datatypes, module, loader, bdb, builtin
from nanamilang import __version_string__, __project_license__


def main():
    """NanamiLang Eval Main function"""

    parser = argparse.ArgumentParser('NanamiLang Evaluator')
    parser.add_argument('-a', '--arg', help='A program argument', action='append')
    parser.add_argument('program',
                        help='Path to source code', nargs='?', default='/dev/stdin')
    parser.add_argument('-e', help='Evaluate one-liner', required=False, default='')
    parser.add_argument('--include-traceback',
                        help='Show exception traceback', action='store_true', default=False)
    parser.add_argument('--show-measurements',
                        help='Show the main module stats', action='store_true', default=False)
    parser.add_argument('--license',
                        help='Show license of NanamiLang', action='store_true', default=False)
    parser.add_argument('--version',
                        help='Show version of NanamiLang', action='store_true', default=False)
    args = parser.parse_args()

    # GNU GPL v2 may require these options

    if args.version:
        print('NanamiLang', __version_string__)
        return 0

    if args.license:
        print('License is', __project_license__)
        return 0

    if not os.path.exists(args.program):
        print('File with source code does not exist')
        return 1

    if args.e:
        inp = args.e
        args.program = '<stdin>'
    else:
        with open(args.program, encoding='utf-8') as r:
            inp = r.read()

    if not inp:
        print('A program source code could not be an empty string')
        return 1

    if not os.environ.get('NANAMILANG_PATH'):
        print('\nNANAMILANG_PATH environment variable has not been set!\n')

    # Initialize NanamiLang Module Loader
    loader.Loader.initialize(
        module.Module,
        loader.LocalIOLoader,
        includetb=args.include_traceback,
        base=os.path.dirname(args.program))

    # Initialize NanamiLang Builtin Database
    bdb.BuiltinMacrosDB.initialize(builtin.BuiltinMacros)
    bdb.BuiltinFunctionsDB.initialize(builtin.BuiltinFunctions)

    module_name = args.program.split('/')[-1].replace('.nml', '')

    m = module.Module(module_name, source=inp)
    if m.state().state() == module.Module.ModuleState.StateIncomplete:
        print('Could not evaluate because module in <StateIncomplete>')
        return 1

    m.evaluate()

    error_list = [d_type.format(include_traceback=args.include_traceback)
                  for d_type in m.results() if d_type.name == 'NException']

    if error_list:

        print(args.program, 'has errors, solve them, before trying again\n')

        for error in error_list:
            print(truncated(error, 67))  # and print each collected error out
        return 1

    nml_main = m.environ().get('main')
    if not nml_main:
        print(args.program, 'has no "main" function. You need to define one')
        return 1

    if args.arg:  # remark: use singular form, but actually 'args.arg' is a _list_
        args_module = module.Module('<args>', ' '.join(args.arg))  # the same here
        if args_module.state().state() == module.Module.ModuleState.StateIncomplete:
            print('WARN: unable to forward passed arguments to the NanamiLang program')
        if args_module.evaluate().broken():
            print('WARN: some of the arguments raised an exception, unable to forward')
        m.environ().set('args', Vector(args_module.evaluate().results()))  # <- store args

    try:
        result = nml_main.reference()([])  # <- actually call current module main function
        frmt = result.format()
        assert isinstance(result, (datatypes.IntegerNumber, datatypes.NException)), (
            f'{args.program}:main: returned non-integer number result, but {frmt} instead!'
        )
    except (Exception,) as e:
        result = datatypes.NException((e, (m.name(), 1, 1)))  # <- make NException instance

    # Be strict, require program main function to return integer number, and no exceptions!

    if isinstance(result, datatypes.NException):
        print('\b', truncated(result.format(include_traceback=args.include_traceback), 67))
        return 1

    if args.show_measurements:
        print('\n'.join(
            [aligned(s, f'{t:.5f} secs.', 67, dots='.') for s, t in m.measurements().items()]))

    return result.reference()

    # Return exit code to system and exit NanamiLang Evaluator script after evaluating a source


if __name__ == "__main__":
    sys.exit(main())
