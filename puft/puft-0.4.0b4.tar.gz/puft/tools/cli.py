import os
import sys
import argparse
import importlib.util
from typing import get_args

from warepy import (
    format_message, join_paths, log, match_enum_containing_value,
    get_enum_values, get_union_enum_values
)

from .. import __version__ as puft_version
from .assembler import Assembler
from ..constants.hints import CLIModeEnumUnion
from ..constants.enums import (
    CLIRunEnum, CLIDatabaseEnum, CLIHelperEnum
)


def main() -> None:
    args = parse_input()

    if args.check_version:
        print(f"Puft {puft_version}")
        return
    elif args.mode[0] in get_union_enum_values(CLIModeEnumUnion):
        mode = args.mode[0] 

        # Find enum where mode assigned.
        mode_enum_class = match_enum_containing_value(
            mode, *get_args(CLIModeEnumUnion))

        # Create according enum with mode value.
        mode_enum = mode_enum_class(mode)
    else:
        raise NotImplementedError(f"Command {args.mode[0]} is not supported")
        # Mode is probably targeted to custom command.
        mode_enum = CLIHelperEnum.CUSTOM_CMD
        #!! custom_cmd = 

    # Create and build assembler.
    assembler = spawn_assembler(
        mode_enum=mode_enum,
        host=args.host,
        port=int(args.port),
        root_dir=args.root_dir,
        source_file=args.source_file,
    )
    assembler.build()

    if type(mode_enum) in get_args(CLIModeEnumUnion):
        # Call appropriate actions depend on chosen mode.
        if type(mode_enum) is CLIRunEnum:
            invoke_run(assembler)
        elif type(mode_enum) is CLIDatabaseEnum:
            with assembler.get_puft().get_native_app().app_context():
                invoke_database_change(assembler, mode_enum)
        elif type(mode_enum) is CLIHelperEnum:
            if mode_enum is CLIHelperEnum.SHELL:
                invoke_shell(assembler)
            elif mode_enum is CLIHelperEnum.CUSTOM_CMD: 
                # TODO: Custom cmds after assembler build operations.
                pass
            elif mode_enum is CLIHelperEnum.DEPLOY:
                # TODO: Implement deploy operation.
                pass

def invoke_shell(assembler: Assembler):
    """Invoke Puft interactive shell."""
    assembler.get_puft().run_shell()

def spawn_assembler(
    mode_enum: CLIModeEnumUnion, host: str, port: int, root_dir: str, source_file: str
) -> Assembler:
    """Create assembler with required parameters and return it."""
    # Add root_dir to sys.path to avoid ModuleNotFoundError during lib importing.
    sys.path.append(root_dir)

    # Load target module spec from location, where cli were called.
    module_location = os.path.join(root_dir, source_file + ".py")
    module_spec = importlib.util.spec_from_file_location(source_file, module_location)
    if module_spec and module_spec.loader:
        main_module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(main_module)
        build = main_module.build
        assembler = Assembler(
            build=build,
            mode_enum=mode_enum,
            host=host,
            port=port
        )
        return assembler
    else:
        raise NameError(format_message("Could not resolve module spec for location: {}.", module_location))


def invoke_run(
    assembler: Assembler
) -> None:
    """"""
    assembler.get_puft().run()


def invoke_database_change(
    assembler: Assembler,
    mode_enum: CLIDatabaseEnum
) -> None:
    db = assembler.get_database()

    if mode_enum is CLIDatabaseEnum.INIT:
        db.init_migration()
    elif mode_enum is CLIDatabaseEnum.MIGRATE:
        db.migrate_migration()
    elif mode_enum is CLIDatabaseEnum.UPGRADE:
        db.upgrade_migration()


def parse_input() -> argparse.Namespace:
    """Parse cli input and return argparse.Namespace object."""
    # TODO: Add help descriptions to args.
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="*")
    parser.add_argument("-a", dest="host", default="127.0.0.1")
    parser.add_argument("-p", dest="port", default="5000")  # TODO: Add check if given port is integer.
    parser.add_argument("-dir", dest="root_dir", default=os.getcwd())
    parser.add_argument("-src", dest="source_file", default="build")
    parser.add_argument("-v", "--version", action="store_true", dest="check_version")
    return parser.parse_args()


if __name__ == "__main__":
    main()
