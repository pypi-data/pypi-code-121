from __future__ import annotations

import argparse
import logging
from typing import Any, Optional

from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi, get_list_from_args

logger = logging.getLogger(__name__)


class DeleteworkspaceMember:
    def __init__(
        self,
        annowork_service: AnnoworkResource,
        workspace_id: str,
    ):
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def main(self, user_id_list: list[str]):
        workspace_members = self.annowork_service.api.get_workspace_members(self.workspace_id)
        member_dict: dict[str, dict[str, Any]] = {m["user_id"]: m for m in workspace_members}
        success_count = 0

        logger.info(f"{len(user_id_list)} 件のユーザをワークスペースメンバから削除します。")
        for user_id in user_id_list:
            member = member_dict.get(user_id)
            if member is None:
                logger.warning(f"{user_id=}: ユーザがワークスペースメンバに存在しません。")
                continue

            try:
                workspace_member_id = member["workspace_member_id"]
                self.annowork_service.api.delete_workspace_member(
                    self.workspace_id, workspace_member_id=workspace_member_id
                )
                success_count += 1
            except Exception as e:
                logger.warning(f"{user_id=}: ワークスペースメンバの削除に失敗しました。{e}")
                continue

        logger.info(f"{success_count}/{len(user_id_list)} 件のユーザをワークスペースメンバから削除しました。")


def main(args):
    annowork_service = build_annoworkapi(args)

    user_id_list = get_list_from_args(args.user_id)
    assert user_id_list is not None
    DeleteworkspaceMember(
        annowork_service=annowork_service,
        workspace_id=args.workspace_id,
    ).main(user_id_list=user_id_list)


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        required=True,
        help="対象のワークスペースID",
    )

    parser.add_argument(
        "-u",
        "--user_id",
        type=str,
        nargs="+",
        required=True,
        help="ワークスペースメンバに追加するuser_id",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "delete"
    subcommand_help = "ワークスペースメンバを削除します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
