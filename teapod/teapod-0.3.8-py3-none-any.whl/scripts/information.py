#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os
import subprocess

from rich.console import Console
from rich.markdown import Markdown


def parse_stdout(commands, failed_message="NOT AVAILABLE"):
    try:
        text = subprocess.run(
            commands,
            text=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        text = failed_message

    return text


class Command(object):
    def __init__(self, markdown_kwargs=None) -> None:
        if not markdown_kwargs:
            markdown_kwargs = {}
        self.markdown_kwargs = markdown_kwargs

    def _add_section(self, lines):
        return Markdown("\n".join(lines), **self.markdown_kwargs)

    def print_system_info(self):
        lines = [
            "# System",
            f'- IP: {parse_stdout(["curl", "-s", "ip.gs"])}',
            f"- Time: {datetime.datetime.now().isoformat()}",
        ]

        return self._add_section(lines)

    def print_path(self):
        lines = ["# Path"] + [f"- {path}" for path in os.getenv("PATH", "").split(":")]

        return self._add_section(lines)

    def print_proxy(self):
        keys = [
            "http_proxy",
            "https_proxy",
            "all_proxy",
        ]
        pairs = ((key, os.getenv(key, "")) for key in keys + list(map(str.upper, keys)))

        lines = ["# Proxy"] + [f"- {key}: {value}" for key, value in pairs if value]

        return self._add_section(lines)

    def print_python_env(self):
        keys = [
            "VIRTUAL_ENV",
            "POETRY_ACTIVE",
        ]
        pairs = ((key, os.getenv(key, "")) for key in keys)

        lines = ["# Python"] + [f"- {key}: {value}" for key, value in pairs]
        lines += [f'- asdf[Python]: {parse_stdout(["asdf", "current", "python"])}']

        return self._add_section(lines)

    def print_git(self):
        lines = [
            "# Git",
            f'- Branch: {parse_stdout(["git", "branch", "--show-current"])}',
            f'- Log: {parse_stdout(["git", "--no-pager", "log", "--pretty=oneline", "--abbrev-commit", "-1"])}',
        ]

        return self._add_section(lines)

    def run(self):
        console = Console()
        console.print(self.print_system_info())
        console.print(self.print_path())
        console.print(self.print_proxy())
        console.print(self.print_python_env())
        console.print(self.print_git())


def main():
    Command().run()


if __name__ == "__main__":
    main()
