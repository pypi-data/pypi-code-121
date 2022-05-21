from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Collection, Optional

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


class Listworkspace:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str):
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def set_additional_info(self, workspace_members: list[dict[str, Any]]):
        logger.debug(f"{len(workspace_members)} 件のメンバのワークスペースタグ情報を取得します。")
        for member in workspace_members:
            workspace_tags = self.annowork_service.api.get_workspace_member_tags(
                self.workspace_id, member["workspace_member_id"]
            )
            member["workspace_tag_ids"] = [e["workspace_tag_id"] for e in workspace_tags]
            member["workspace_tag_names"] = [e["workspace_tag_name"] for e in workspace_tags]

    def get_workspace_members_from_tags(self, workspace_tag_ids: Collection[str]) -> list[dict[str, Any]]:
        result = []
        for tag_id in workspace_tag_ids:
            tmp = self.annowork_service.api.get_workspace_tag_members(self.workspace_id, tag_id)
            result.extend(tmp)

        # メンバが重複している可能性があるので取り除く
        # pandasのメソッドを使うために、一時的にDataFrameにする
        return pandas.DataFrame(result).drop_duplicates().to_dict("records")

    def main(
        self,
        output: Path,
        output_format: OutputFormat,
        workspace_tag_ids: Optional[Collection[str]],
        show_workspace_tag: bool,
    ):
        if workspace_tag_ids is not None:
            workspace_members = self.get_workspace_members_from_tags(workspace_tag_ids)
        else:
            workspace_members = self.annowork_service.api.get_workspace_members(
                self.workspace_id, query_params={"includes_inactive_members": True}
            )

        if show_workspace_tag:
            self.set_additional_info(workspace_members)

        workspace_members.sort(key=lambda e: e["user_id"].lower())

        if len(workspace_members) == 0:
            logger.warning(f"ワークスペースメンバ情報は0件なので、出力しません。")
            return

        logger.debug(f"{len(workspace_members)} 件のワークスペースメンバ一覧を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(workspace_members, is_pretty=True, output=output)
        else:
            df = pandas.json_normalize(workspace_members)
            print_csv(df, output=output)


def main(args):
    annowork_service = build_annoworkapi(args)
    workspace_tag_id_list = get_list_from_args(args.workspace_tag_id)
    Listworkspace(annowork_service=annowork_service, workspace_id=args.workspace_id).main(
        output=args.output,
        output_format=OutputFormat(args.format),
        workspace_tag_ids=workspace_tag_id_list,
        show_workspace_tag=args.show_workspace_tag,
    )


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        required=True,
        help="対象のワークスペースID",
    )

    parser.add_argument(
        "-wt",
        "--workspace_tag_id",
        nargs="+",
        type=str,
        help="指定したワークスペースタグが付与されたワークスペースメンバを出力します。",
    )

    parser.add_argument(
        "--show_workspace_tag",
        action="store_true",
        help="ワークスペースタグに関する情報も出力します。",
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
    subcommand_help = "ワークスペースメンバの一覧を出力します。無効化されたメンバも出力します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
