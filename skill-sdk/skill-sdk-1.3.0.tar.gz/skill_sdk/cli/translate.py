#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""CLI: "translate" command"""

import argparse


def execute(args: argparse.Namespace) -> None:
    """
    Extract translations from Python modules,
    optionally can download translations from the text service

    :param args:
    :return:
    """
    from skill_sdk.config import settings
    from skill_sdk.tools.translate import download_translations, extract_translations

    #
    # If download URL specified, download translations from text services and save locally:
    # this is a step to migrate skills and decommission the service
    #
    # Once skills are migrated, this function becomes obsolete
    #
    if args.download_url:
        download_translations(
            args.download_url,
            settings.SKILL_NAME,
            args.token,
            args.tenant,
            args.force,
        )

    else:
        extract_translations(args.modules)


def add_subparser(subparsers) -> None:
    """
    Command arguments parser

    :param subparsers:
    :return:
    """

    translate_parser = subparsers.add_parser(
        "translate",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Translate a project.",
        description="Extracts translatable strings from Python modules. "
        "Creates translation catalog 'messages.pot'."
        "Optionally, downloads full catalog from text service and "
        "saves translations in YAML format as '{locale}.yaml'",
    )

    translate_parser.add_argument(
        "modules",
        nargs="*",
        default=["impl"],
        help="Modules to scan and translate (multiple values are supported, i.e.: 'impl app.py').",
    )

    translate_parser.add_argument(
        "-d",
        "--download-url",
        help="URL to download the translations catalog (text services URL).",
        action="store",
        type=str,
        nargs="?",
    )

    translate_parser.add_argument(
        "-k",
        "--token",
        help="Bearer authentication token (for the text services).",
        action="store",
        type=str,
        nargs="?",
    )

    translate_parser.add_argument(
        "-n",
        "--tenant",
        help="Tenant (for admin route authentication)",
        action="store",
        type=str,
        nargs="?",
    )

    translate_parser.add_argument(
        "-f",
        "--force",
        help="Overwrite existing translations.",
        action="store_const",
        dest="force",
        const=True,
    )

    translate_parser.set_defaults(command=execute)
