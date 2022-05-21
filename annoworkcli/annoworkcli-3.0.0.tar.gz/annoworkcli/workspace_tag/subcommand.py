import argparse
from typing import Optional

import annoworkcli
import annoworkcli.workspace_tag.list_workspace_tag
import annoworkcli.workspace_tag.put_workspace_tag


def parse_args(parser: argparse.ArgumentParser):

    subparsers = parser.add_subparsers(dest="subcommand_name")

    # サブコマンドの定義
    annoworkcli.workspace_tag.list_workspace_tag.add_parser(subparsers)
    annoworkcli.workspace_tag.put_workspace_tag.add_parser(subparsers)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "workspace_tag"
    subcommand_help = "ワークスペースタグ関係のサブコマンド"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help, is_subcommand=False
    )
    parse_args(parser)
    return parser
