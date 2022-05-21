from __future__ import annotations

import argparse
import logging
from typing import Optional

from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi

logger = logging.getLogger(__name__)


class Putworkspace:
    def __init__(
        self,
        annowork_service: AnnoworkResource,
    ):
        self.annowork_service = annowork_service

    def main(self, workspace_id: str, workspace_name: str, email: str):
        org = self.annowork_service.wrapper.get_workspace_or_none(workspace_id)

        request_body = {
            "workspace_name": workspace_name,
            "email": email,
        }
        if org is not None:
            request_body["last_updated_datetime"] = org["updated_datetime"]

        self.annowork_service.api.put_workspace(workspace_id, request_body=request_body)

        logger.info(f"ワークスペース {workspace_id} を作成/更新しました。")


def main(args):
    annowork_service = build_annoworkapi(args)

    Putworkspace(
        annowork_service=annowork_service,
    ).main(workspace_id=args.workspace_id, workspace_name=args.workspace_name, email=args.email)


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        required=True,
        help="対象のワークスペースID",
    )

    parser.add_argument(
        "--workspace_name",
        type=str,
        required=True,
        help="ワークスペース名",
    )

    parser.add_argument(
        "--email",
        type=str,
        required=True,
        help="ワークスペース管理者のe-mailアドレス",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "put"
    subcommand_help = "ワークスペースを登録/更新します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
