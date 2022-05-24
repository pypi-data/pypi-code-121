# -*- coding: utf-8 -*-

import argparse

from tuxsuite.cli.version import __version__

from tuxsuite.cli.build import setup_parser as build_parser
from tuxsuite.cli.plan import setup_parser as plan_parser
from tuxsuite.cli.test import setup_parser as test_parser


def setup_parser(group, project):
    parser = argparse.ArgumentParser(prog="tuxsuite", description="tuxsuite")

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s, {__version__}"
    )

    parser.add_argument("--group", default=group)
    parser.add_argument("--project", default=project)

    root = parser.add_subparsers(dest="sub_command", help="Sub commands")
    root.required = True

    # "build"
    build = root.add_parser("build", help="builds").add_subparsers(
        dest="sub_sub_command", help="Sub commands"
    )
    build.required = True
    build_parser(build)

    # "plan"
    plan = root.add_parser("plan", help="plans").add_subparsers(
        dest="sub_sub_command", help="Sub commands"
    )
    plan.required = True
    plan_parser(plan)

    # "test"
    test = root.add_parser("test", help="tests").add_subparsers(
        dest="sub_sub_command", help="Sub commands"
    )
    test.required = True
    test_parser(test)

    return parser
