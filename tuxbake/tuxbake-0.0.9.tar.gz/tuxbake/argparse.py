#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
from tuxmake.runtime import Runtime
from typing import List


class supported:
    runtimes: List[str] = Runtime.supported()


##########
# Setups #
##########
def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tuxbake", description="TuxBake")
    #    parser.add_argument(
    #    "--version", action="version", version=f"%(prog)s, {__version__}"
    # )
    group = parser.add_argument_group("OE Build Parameters")
    group.add_argument(
        "--build-definition",
        help="Specify json file with build parameters",
        required=True,
    )
    group.add_argument(
        "--build-only",
        help="Assume the source tree is already pulled.",
        action="store_true",
    )
    group.add_argument(
        "--debug",
        help="Provides extra output on stderr for debugging tuxbake itself. This output will not appear in the build log.",
        action="store_true",
    )
    group.add_argument(
        "-r",
        "--runtime",
        help=f"Runtime to use for the builds. By default, builds are run in a docker container. With 'docker-local' runtime the --image option needs to be specified to a local container. Supported: {', '.join(supported.runtimes)}.",
        default="docker",
    )
    group.add_argument(
        "-i",
        "--image",
        help="Image to build with, for container-based runtimes (docker etc). Implies --runtime=docker if no runtime is explicit specified. (default: tuxbake-provided images).",
        default=None,
    )
    group.add_argument(
        "--src-dir",
        help="source directory where the sources will be downloaded",
    )
    group.add_argument(
        "--sync-only",
        help="Download all the meta repositories via repo or git only.",
        action="store_true",
    )
    group.add_argument(
        "--build-dir-name",
        help="Directory name passed to the source script during OE build. It defaults to build",
        default="build",
    )
    group.add_argument(
        "--local-manifest",
        help="Path to a local manifest file which will be used during repo sync. This input is ignored if sources used is git_trees in the build definition",
        default=None,
    )
    group.add_argument(
        "--pinned-manifest",
        help="Path to a local manifest file which will be used to override repo setup before doing repo sync. This input is ignored if sources used is git_trees in the build definition",
        default=None,
    )
    return parser
