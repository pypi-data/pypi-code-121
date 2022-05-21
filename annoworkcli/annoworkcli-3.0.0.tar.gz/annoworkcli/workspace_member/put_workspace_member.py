from __future__ import annotations

import argparse
import logging
import uuid
from typing import Any, Collection, Optional

from annoworkapi.enums import Role
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi, get_list_from_args

logger = logging.getLogger(__name__)


class PutworkspaceMember:
    def __init__(
        self,
        annowork_service: AnnoworkResource,
        workspace_id: str,
    ):
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def put_workspace_member(
        self,
        user_id: str,
        role: str,
        workspace_tag_id_list: Optional[Collection[str]],
        old_member: Optional[dict[str, Any]],
    ):
        """[summary]

        Args:
            user_id (str): [description]
            role (str): [description]
            workspace_tag_id_list (Optional[list[str]]): [description]
            old_member (Optional[dict[str,Any]]): [description]
        """
        last_updated_datetime = None
        if old_member is not None:
            last_updated_datetime = old_member["updated_datetime"]
            workspace_member_id = old_member["workspace_member_id"]

        else:
            last_updated_datetime = None
            workspace_member_id = str(uuid.uuid4())

        request_body: dict[str, Any] = {
            "user_id": user_id,
            "role": role,
            "workspace_tags": workspace_tag_id_list if workspace_tag_id_list is not None else [],
        }
        if last_updated_datetime is not None:
            request_body["last_updated_datetime"] = last_updated_datetime

        new_member = self.annowork_service.api.put_workspace_member(
            self.workspace_id, workspace_member_id, request_body=request_body
        )
        logger.debug(f"{user_id=} :: ワークスペースメンバを追加しました。 :: username='{new_member['username']}', {workspace_member_id=}")
        return True

    def main(self, user_id_list: list[str], role: str, workspace_tag_id_list: Optional[Collection[str]]):
        workspace_members = self.annowork_service.api.get_workspace_members(
            self.workspace_id, query_params={"includes_inactive_members": True}
        )
        member_dict: dict[str, dict[str, Any]] = {m["user_id"]: m for m in workspace_members}
        success_count = 0
        for user_id in user_id_list:
            try:
                result = self.put_workspace_member(
                    user_id,
                    role,
                    workspace_tag_id_list=workspace_tag_id_list,
                    old_member=member_dict.get(user_id),
                )
                if result:
                    success_count += 1
            except Exception:
                logger.warning(f"{user_id=}: ワークスペースメンバの登録に失敗しました。", exc_info=True)
                continue

        logger.info(f"{success_count}/{len(user_id_list)} 件のユーザをワークスペースメンバに登録しました。")


def main(args):
    annowork_service = build_annoworkapi(args)
    user_id_list = get_list_from_args(args.user_id)
    workspace_tag_id_list = get_list_from_args(args.workspace_tag_id)
    assert user_id_list is not None
    PutworkspaceMember(
        annowork_service=annowork_service,
        workspace_id=args.workspace_id,
    ).main(user_id_list=user_id_list, role=args.role, workspace_tag_id_list=workspace_tag_id_list)


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

    parser.add_argument(
        "-wt",
        "--workspace_tag_id",
        type=str,
        nargs="+",
        required=False,
        help="メンバに付与するワークスペースタグID",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "put"
    subcommand_help = "ワークスペースメンバを登録します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
