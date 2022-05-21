import argparse
import logging
from pathlib import Path
from typing import Optional

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


class ListworkspaceMember:
    def __init__(self, annowork_service: AnnoworkResource):
        self.annowork_service = annowork_service

    def main(self, output: Optional[Path], output_format: OutputFormat, workspace_id: Optional[str] = None):
        query_params = {}
        if workspace_id is not None:
            query_params[workspace_id] = workspace_id

        my_workspace_members = self.annowork_service.api.get_my_workspace_members(query_params=query_params)

        if len(my_workspace_members) == 0:
            logger.warning(f"ワークスペースメンバ情報は0件なので、出力しません。")
            return

        logger.debug(f"{len(my_workspace_members)} 件のワークスペースメンバ一覧を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(my_workspace_members, is_pretty=True, output=output)
        else:
            df = pandas.json_normalize(my_workspace_members)
            print_csv(df, output=output)


def main(args):
    annowork_service = build_annoworkapi(args)
    ListworkspaceMember(annowork_service=annowork_service).main(
        output=args.output, output_format=OutputFormat(args.format)
    )


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument("-o", "--output", type=Path, help="出力先")
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        choices=[e.value for e in OutputFormat],
        help="出力先のフォーマット",
        default=OutputFormat.CSV.value,
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "list_workspace_member"
    subcommand_help = "自身のワークスペースメンバの一覧を出力します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
