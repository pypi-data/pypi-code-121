import sys

from pathlib import Path
from pprint import pformat

from clmgr.args import (
    handle_config_file,
    handle_debug,
    handle_input_dir,
    handle_version,
    parse_args,
    read_config,
)
from clmgr.log import setup_custom_logger
from clmgr.processor import process_lines


log = setup_custom_logger("root")


class ContinueIgnore(Exception):
    pass


def main(argv):
    if argv is not None:
        args = parse_args(argv)
    else:
        args = parse_args(sys.argv[1:])

    handle_version(args)
    handle_debug(args, log)
    config_file = handle_config_file(args)
    input_dir = handle_input_dir(args)

    # Load Configuration
    cfg = read_config(config_file)
    log.debug(f"Configuration:\n{pformat(cfg, indent=2)}")

    # Process Input
    # Input can be one of the following:
    #  * file
    #  * directory
    # however please note that the configuration must always be provided either present from
    # the current working directory or through the flag -c, --config
    add = 0
    upd = 0

    for ext in cfg["source"]:
        # Find all files for provided source extension
        file_list = []
        continue_ignore = ContinueIgnore()

        if args.file is not None:
            path = Path(args.file)
            if path.suffix.lower()[1:] == ext:
                file_list.append(path)
        else:
            file_list = Path(input_dir).rglob(f"*.{ext}")

        for p in file_list:
            try:
                if "exclude" in cfg:
                    for exclude in cfg["exclude"]:
                        if p.stem == exclude:
                            log.debug(f"Excluding file {p}; match: {exclude}")
                            raise continue_ignore
                        if p.name == exclude:
                            log.debug(f"Excluding file {p}; match: {exclude}")
                            raise continue_ignore
                        if p.match(exclude):
                            log.debug(f"Excluding file {p}; match: {exclude}")
                            raise continue_ignore
            except ContinueIgnore:
                continue

            log.debug(f"Processing file: {p}")

            # Read source and close it
            src = open(p.absolute())
            lines = src.readlines()
            src.close()

            # Process file
            res = process_lines(cfg, p, ext, lines, args)
            add += res[0]
            upd += res[1]

    print(f"[{add}] Copyright added")
    print(f"[{upd}] Copyright Updated")
