#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json

from tuxbake.models import OEBuild
from tuxbake.argparse import setup_parser
from tuxbake.build import build
from tuxbake.exceptions import (
    TuxbakeParsingError,
    TuxbakeRunCmdError,
)

##############
# Entrypoint #
##############
def main() -> int:
    # Parse command line
    parser = setup_parser()
    options = parser.parse_args()
    with open(options.build_definition) as reader:
        try:
            build_definition = json.load(reader)
            legacy_target = build_definition.get("target")
            targets = build_definition.get("targets")
            if legacy_target:
                if targets is None:
                    build_definition["targets"] = legacy_target
                del build_definition["target"]
            OEBuild.validate(build_definition)
            build(
                **(build_definition),
                src_dir=options.src_dir,
                build_dir=options.build_dir_name,
                local_manifest=options.local_manifest,
                pinned_manifest=options.pinned_manifest,
                runtime=options.runtime,
                image=options.image,
                debug=options.debug,
                build_only=options.build_only,
                sync_only=options.sync_only,
            )
        except (TuxbakeParsingError, TuxbakeRunCmdError) as ex:
            sys.stderr.write(f"{str(ex)}\n")
            sys.exit(1)


def start():
    if __name__ == "__main__":
        sys.exit(main())


start()
