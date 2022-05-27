# -*- coding: utf-8 -*-

import argparse
import json
import os
import re
import sys


class ConfigParser(object):
    def __init__(self, config_file) -> None:
        self.config_file = config_file
        self._read()

    def _read(self):
        with open(self.config_file, mode="r", encoding="utf-8") as f:
            servers = []
            parsed = False
            for line in f:
                line = line.rstrip()
                if line == "[Proxy]":
                    parsed = True
                elif re.match(r"\[.+\]", line) and parsed:
                    break
                elif match := re.match(
                    r"(?P<name>[^,]+)\s*=\s*(?P<type>\S+)\s*,\s*(?P<host>\S+)\s*,\s*(?P<port>\d+)\s*,\s*(?P<options>.+)",
                    line,
                ):
                    host = match["host"]
                    if host in ("localhost", "127.0.0.1"):
                        continue

                    port = int(match["port"])
                    raw_options = match["options"].split(",")
                    options = {}
                    for raw_option in raw_options:
                        key, value = raw_option.strip().split("=")
                        options[key] = value
                    servers += [
                        {
                            "address": host,
                            "port": port,
                            "method": options["encrypt-method"],
                            "password": options["password"],
                        }
                    ]

        self.servers = servers

    def to_dict(self, local_host="127.0.0.1", local_port=1080):
        return {
            "servers": self.servers,
            "local_host": local_host,
            "local_port": local_port,
        }


def write_json(obj, filename):
    with open(filename, mode="w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--surge_config",
        type=str,
        default=os.path.expanduser(
            "~/Library/Mobile Documents/iCloud~com~nssurge~inc/Documents/Surge3.conf"
        )
        if sys.platform == "darwin"
        else None,
    )
    parser.add_argument("--ss_config", type=str, default="./ss.config")
    parser.add_argument("--local_host", type=str, default="127.0.0.1")
    parser.add_argument("--local_port", type=str, default=1080)

    return parser.parse_args()  # pylint: disable=redefined-outer-name


def main():
    args = parse_args()
    config_parser = ConfigParser(args.surge_config)
    config = config_parser.to_dict(
        local_host=args.local_host, local_port=args.local_port
    )
    write_json(config, args.ss_config)


if __name__ == "__main__":
    main()
