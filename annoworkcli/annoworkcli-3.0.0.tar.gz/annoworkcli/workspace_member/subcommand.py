import argparse
from typing import Optional

import annoworkcli
import annoworkcli.workspace_member.append_tag_to_workspace_member
import annoworkcli.workspace_member.change_workspace_member_properties
import annoworkcli.workspace_member.delete_workspace_member
import annoworkcli.workspace_member.list_workspace_member
import annoworkcli.workspace_member.put_workspace_member
import annoworkcli.workspace_member.remove_tag_to_workspace_member


def parse_args(parser: argparse.ArgumentParser):

    subparsers = parser.add_subparsers(dest="subcommand_name")

    # サブコマンドの定義
    annoworkcli.workspace_member.append_tag_to_workspace_member.add_parser(subparsers)
    annoworkcli.workspace_member.change_workspace_member_properties.add_parser(subparsers)
    annoworkcli.workspace_member.delete_workspace_member.add_parser(subparsers)
    annoworkcli.workspace_member.list_workspace_member.add_parser(subparsers)

    annoworkcli.workspace_member.put_workspace_member.add_parser(subparsers)
    annoworkcli.workspace_member.remove_tag_to_workspace_member.add_parser(subparsers)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "workspace_member"
    subcommand_help = "ワークスペースメンバ関係のサブコマンド"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help, is_subcommand=False
    )
    parse_args(parser)
    return parser
