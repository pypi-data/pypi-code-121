from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Optional

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


class Listworkspace:
    def __init__(
        self,
        annowork_service: AnnoworkResource,
    ):
        self.annowork_service = annowork_service

    def get_workspace_list(
        self,
        workspace_id_list: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        if workspace_id_list is None:
            return self.annowork_service.api.get_my_workspaces()

        workspace_list = []
        for workspace_id in workspace_id_list:
            org = self.annowork_service.wrapper.get_workspace_or_none(workspace_id)
            if org is None:
                logger.warning(f"{workspace_id=} であるワークスペースは存在しませんでした。")
                continue
            workspace_list.append(org)
        return workspace_list

    def main(
        self,
        output: Path,
        output_format: OutputFormat,
        *,
        workspace_id_list: Optional[list[str]],
    ):
        workspace_list = self.get_workspace_list(workspace_id_list)
        if len(workspace_list) == 0:
            logger.warning(f"ワークスペース情報は0件なので、出力しません。")
            return

        logger.debug(f"{len(workspace_list)} 件のワークスペース一覧を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(workspace_list, is_pretty=True, output=output)
        else:
            df = pandas.DataFrame(workspace_list)
            print_csv(df, output=output)


def main(args):
    annowork_service = build_annoworkapi(args)
    workspace_id_list = get_list_from_args(args.workspace_id)
    Listworkspace(
        annowork_service=annowork_service,
    ).main(output=args.output, output_format=OutputFormat(args.format), workspace_id_list=workspace_id_list)


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        nargs="+",
        required=False,
        help="対象のワークスペースIDを指定してください。未指定の場合は、自身の所属しているワークスペース一覧を出力します。",
    )

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
    subcommand_name = "list"
    subcommand_help = "ワークスペースの一覧を取得します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
