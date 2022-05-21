import argparse
from typing import Optional

import annoworkcli
import annoworkcli.workspace.list_workspace
import annoworkcli.workspace.put_workspace
from annoworkcli.common.cli import add_parser as add_root_parser


def parse_args(parser: argparse.ArgumentParser):

    subparsers = parser.add_subparsers(dest="subcommand_name")
    annoworkcli.workspace.list_workspace.add_parser(subparsers)
    annoworkcli.workspace.put_workspace.add_parser(subparsers)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "workspace"
    subcommand_help = "ワークスペース関係のサブコマンド"

    parser = add_root_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help, is_subcommand=False
    )
    parse_args(parser)
    return parser
