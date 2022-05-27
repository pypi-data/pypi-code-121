#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import datetime
import logging
import os
import shutil
import tempfile

from resworb.browsers.safari import Safari

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--source",
        type=str,
        nargs="+",
        choices=["cloud_tabs", "opened_tabs", "histories", "bookmarks", "readings"],
        default=["cloud_tabs", "readings"],
    )
    parser.add_argument(
        "--inbox",
        type=str,
        default=f"{os.getenv('HOME')}/org/agenda/inbox.org",
    )

    return parser.parse_args()  # pylint: disable=redefined-outer-name


def format_org_heading(url_item, template="* [[{url}][{title}]]\n[{timestamp}]\n"):
    return template.format(
        url=url_item["url"],
        title=url_item["title"],
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %a %H:%M"),
    )


def format_captures(data):
    def _iter(data):
        for source, source_data in data.items():
            if source == "cloud_tabs":
                for device_data in source_data:
                    yield from device_data["tabs"]
            else:
                yield from source_data

    return map(format_org_heading, _iter(data))


def write_to_inbox(captures, inbox_file):
    with open(inbox_file, mode="r") as f:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as g:
            wrote = False
            for line in f:
                line = line.rstrip()

                if not wrote and line.startswith("*"):
                    for item in captures:
                        g.writelines(f"{item}\n")
                    wrote = True

                g.writelines(f"{line}\n")
        shutil.copy(g.name, inbox_file)


def main():
    args = parse_args()

    safari = Safari()
    data = safari.export(args.source)

    captures = format_captures(data)
    write_to_inbox(captures, args.inbox)

    logger.info("Export statistics:")
    for source, source_data in data.items():
        if source == "cloud_tabs":
            logger.info("%s\t%d", source, sum(len(x["tabs"]) for x in source_data))
        else:
            logger.info("%s\t%d", source, len(source_data))

    if {"cloud_tabs", "opened_tabs", "readings"} & set(args.source):
        logger.info("Be sure to close exported tabs to avoid duplicates next time!")


if __name__ == "__main__":
    main()
