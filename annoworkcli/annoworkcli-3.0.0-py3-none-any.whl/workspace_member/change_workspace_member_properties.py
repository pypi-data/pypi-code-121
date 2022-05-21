from __future__ import annotations

import argparse
import logging
from typing import Any, Collection, Optional

from annoworkapi.enums import Role
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi, get_list_from_args

logger = logging.getLogger(__name__)


class ChangeworkspaceMemberProperties:
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
        role: str,
        old_workspace_tag_ids: Collection[str],
        old_member: dict[str, Any],
    ) -> bool:
        workspace_member_id = old_member["workspace_member_id"]

        request_body: dict[str, Any] = {
            "user_id": user_id,
            "role": role,
            "workspace_tags": list(old_workspace_tag_ids),
            "last_updated_datetime": old_member["updated_datetime"],
        }

        new_member = self.annowork_service.api.put_workspace_member(
            self.workspace_id, workspace_member_id, request_body=request_body
        )
        logger.debug(f"{user_id=}, {workspace_member_id=}: ワークスペースメンバのロールを変更しました。 :: {new_member}")
        return True

    def main(self, user_id_list: list[str], role: str):
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

                if old_member["role"] == role:
                    logger.warning(f"{user_id=} のロールは '{role}' なので、ロールを変更する必要はありません。スキップします。")
                    continue

                old_tags = self.annowork_service.api.get_workspace_member_tags(
                    self.workspace_id, old_member["workspace_member_id"]
                )
                old_workspace_tag_ids = {e["workspace_tag_id"] for e in old_tags}

                result = self.put_workspace_member(
                    user_id, role=role, old_workspace_tag_ids=old_workspace_tag_ids, old_member=old_member
                )
                if result:
                    success_count += 1
            except Exception as e:
                logger.warning(f"{user_id=}: ワークスペースメンバの登録に失敗しました。{e}")
                continue

        logger.info(f"{success_count}/{len(user_id_list)} 件のユーザをワークスペースメンバに登録しました。")


def main(args):
    annowork_service = build_annoworkapi(args)
    user_id_list = get_list_from_args(args.user_id)
    assert user_id_list is not None
    ChangeworkspaceMemberProperties(
        annowork_service=annowork_service,
        workspace_id=args.workspace_id,
    ).main(user_id_list=user_id_list, role=args.role)


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

    parser.add_argument(
        "--role",
        type=str,
        choices=[e.value for e in Role],
        required=True,
        help="権限",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "change"
    subcommand_help = "ワークスペースメンバの情報（ロールなど）を変更します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
