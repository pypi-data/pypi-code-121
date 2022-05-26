#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import logging.config
import pathlib
import sys
from pprint import pformat

from dm.commonlib import Common as common
from dm.core.AppExitStatus import AppExitStatus
from dm.iam_policy import IAMService

log = logging.getLogger(__name__)


MIGRATION_PERMISSIONS_SID = "TemporaryMigrationPermissions"
MIGRATION_PERMISSIONS = {
    "Sid": MIGRATION_PERMISSIONS_SID,
    "Effect": "Allow",
    "Action": [
        "ec2:ModifyVpcEndpoint",
        "ec2:DescribeTransitGatewayVpcAttachments",
        "ec2:GetTransitGatewayAttachmentPropagations",
        "ec2:ReplaceRouteTableAssociation",
        "ec2:DisassociateVpcCidrBlock",
        "ec2:DisassociateSubnetCidrBlock",
        "ec2:DetachVpnGateway",
        "ec2:DeleteVpnGateway",
        "directconnect:DeleteVirtualInterface",
    ],
    "Resource": "*",
}


def setup(args, account_data):
    logconf = common.initLogLocation(account_data).logging_config
    logconf["handlers"]["consoleHandler"]["level"] = logging.INFO
    if args.verbose:
        logconf["handlers"]["consoleHandler"]["level"] = logging.DEBUG
        logconf["handlers"]["logConsoleHandler"]["level"] = logging.DEBUG
    logging.config.dictConfig(logconf)

    iargs = " ".join(sys.argv[1:])
    common.logCommandOptions(f"dm.configure_iam {iargs}")
    log.debug("Called with args: \n%s", pformat(vars(args)))


def handle_add(args):
    accounts_data = common.convert_yaml_to_json(args.discovery_config)
    setup(args, accounts_data)

    for account in accounts_data["account_info"]:
        account_iam = IAMService(account)
        succeeded = account_iam.add_permissions(
            MIGRATION_PERMISSIONS, delete_oldest=args.force
        )
        if not succeeded and args.fail_fast:
            return


def handle_rm(args):
    accounts_data = common.convert_yaml_to_json(args.discovery_config)
    setup(args, accounts_data)

    for account in accounts_data["account_info"]:
        account_iam = IAMService(account)
        succeeded = account_iam.remove_permissions(
            MIGRATION_PERMISSIONS_SID, delete_oldest=args.force
        )
        if not succeeded and args.fail_fast:
            return


def main():
    parser = argparse.ArgumentParser(description="Update IAM policies")
    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser(
        "add", help="Add required IAM permissions policy."
    )
    parser_add.set_defaults(handle=handle_add)

    parser_rm = subparsers.add_parser(
        "remove",
        aliases=["rm"],
        help="Remove previously added IAM permissions policy.",
    )
    parser_rm.set_defaults(handle=handle_rm)

    parser.add_argument("discovery_config", action="store", type=pathlib.Path)
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        default=False,
        help="Delete oldest policy if max number of policies exceeded.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        default=False,
        help="Exit immediately on error.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Increase verbosity of the configure_iam script.",
    )

    args = parser.parse_args()
    args.handle(args)
    sys.exit(AppExitStatus().getStatus())


if __name__ == "__main__":
    main()
