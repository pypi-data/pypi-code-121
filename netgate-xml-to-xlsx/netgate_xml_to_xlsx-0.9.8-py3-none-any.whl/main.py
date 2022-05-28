"""Main netgate converstion module."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import sys

import toml

from netgate_xml_to_xlsx.errors import NodeError

from .parse_args import parse_args
from .pfsense import PfSense


def banner(pfsense: PfSense) -> None:
    """Tell people what we're doing."""
    print(f"Output: {pfsense.ss_output_path}.")


def _main() -> None:
    """Driver."""
    args = parse_args()
    in_files = args.in_files
    config = toml.load("./plugins.toml")

    for in_filename in in_files:
        pfsense = PfSense(args, in_filename)
        banner(pfsense)

        if args.sanitize:
            pfsense.sanitize(config["plugins"])
            continue

        # Run plugins in order.
        for plugin_to_run in config["plugins"]:
            print(f"    {plugin_to_run}")
            pfsense.run(plugin_to_run)
        pfsense.save()


def main() -> None:
    """Drive and catch exceptions."""
    try:
        _main()
    except NodeError as err:
        print(err)
        sys.exit(-1)


if __name__ == "__main__":
    main()
