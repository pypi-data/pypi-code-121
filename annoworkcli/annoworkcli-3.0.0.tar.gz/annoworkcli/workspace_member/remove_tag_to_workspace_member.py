from __future__ import annotations

import argparse
import logging
from typing import Any, Collection, Optional

from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi, get_list_from_args

logger = logging.getLogger(__name__)


class RemoveTagToworkspaceMember:
    def __init__(
        self,
        *,
        annowork_service: AnnoworkResource,
        workspace_id: str,
    ):
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def put_workspace_member(
        self,
        user_id: str,
        *,
        old_workspace_tag_ids: Collection[str],
        workspace_tag_ids: Collection[str],
        old_member: dict[str, Any],
    ) -> bool:
        workspace_member_id = old_member["workspace_member_id"]

        new_workspace_tags = list(set(old_workspace_tag_ids) - set(workspace_tag_ids))
        request_body: dict[str, Any] = {
            "user_id": user_id,
            "role": old_member["role"],
            "workspace_tags": new_workspace_tags,
            "last_updated_datetime": old_member["updated_datetime"],
        }

        new_member = self.annowork_service.api.put_workspace_member(
            self.workspace_id, workspace_member_id, request_body=request_body
        )
        logger.debug(f"{user_id=} :: ワークスペースメンバからワークスペースタグを削除しました。 :: username='{new_member['username']}'")
        return True

    def main(self, user_id_list: list[str], workspace_tag_ids: Collection[str]):
        workspace_members = self.annowork_service.api.get_workspace_members(
            self.workspace_id, query_params={"includes_inactive_members": True}
        )
        member_dict: dict[str, dict[str, Any]] = {m["user_id"]: m for m in workspace_members}
        success_count = 0
        for user_id in user_id_list:
            try:
                old_member = member_dict.get(user_id)
                if old_member is None:
                    logger.warning(f"{user_id=} のユーザはワークスペースメンバに存在しないので、スキップします。")
                    continue

                old_tags = self.annowork_service.api.get_workspace_member_tags(
                    self.workspace_id, old_member["workspace_member_id"]
                )
                old_workspace_tag_ids = {e["workspace_tag_id"] for e in old_tags}
                diff_tags = old_workspace_tag_ids - set(workspace_tag_ids)
                if old_workspace_tag_ids == diff_tags:
                    logger.warning(f"{user_id=} には、すでにワークスペースタグ {workspace_tag_ids} が設定されていないので、スキップします。")
                    continue

                result = self.put_workspace_member(
                    user_id,
                    old_workspace_tag_ids=old_workspace_tag_ids,
                    workspace_tag_ids=workspace_tag_ids,
                    old_member=old_member,
                )
                if result:
                    success_count += 1
            except Exception as e:
                logger.warning(f"{user_id=}: ワークスペースタグの削除に失敗しました。{e}", e)
                continue

        logger.info(f"{success_count}/{len(user_id_list)} 件のユーザからワークスペースタグを削除しました。")


def main(args):
    annowork_service = build_annoworkapi(args)
    user_id_list = get_list_from_args(args.user_id)
    workspace_tag_id_list = get_list_from_args(args.workspace_tag_id)
    assert user_id_list is not None
    assert workspace_tag_id_list is not None

    RemoveTagToworkspaceMember(
        annowork_service=annowork_service,
        workspace_id=args.workspace_id,
    ).main(user_id_list=user_id_list, workspace_tag_ids=workspace_tag_id_list)


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
        help="対象ユーザのuser_id",
    )

    parser.add_argument(
        "-wt",
        "--workspace_tag_id",
        type=str,
        nargs="+",
        required=True,
        help="メンバから削除するワークスペースタグID",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "remove_tag"
    subcommand_help = "ワークスペースメンバからワークスペースタグを削除します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
