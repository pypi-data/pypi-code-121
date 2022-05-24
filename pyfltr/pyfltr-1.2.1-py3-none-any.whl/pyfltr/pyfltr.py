#!/usr/bin/env python3
"""pyfltr。"""
from __future__ import annotations

import argparse
import dataclasses
import logging
import os
import pathlib
import shlex
import subprocess
import sys
import threading
import time
import typing

import joblib
import tomli

CONFIG: dict[str, typing.Any] = {
    # コマンド毎に有効無効、パス、追加の引数、対象ファイルパターン
    "pyupgrade": True,
    "pyupgrade-path": "pyupgrade",
    "pyupgrade-args": [],
    "isort": True,
    "isort-path": "isort",
    "isort-args": [],
    "black": True,
    "black-path": "black",
    "black-args": [],
    "pflake8": True,
    "pflake8-path": "pflake8",
    "pflake8-args": [],
    "mypy": True,
    "mypy-path": "mypy",
    "mypy-args": [],
    "pylint": True,
    "pylint-path": "pylint",
    "pylint-args": [],
    "pytest": True,
    "pytest-path": "pytest",
    "pytest-args": [],
    # flake8風無視パターン。
    "exclude": [
        # ここの値はflake8やblackなどの既定値を元に適当に。
        "*.egg",
        ".bzr",
        ".direnv",
        ".eggs",
        ".git",
        ".hg",
        ".mypy_cache",
        ".nox",
        ".pytest_cache",
        ".svn",
        ".tox",
        ".venv",
        "CVS",
        "__pycache__",
        "_build",
        "buck-out",
        "build",
        "dist",
        "venv",
    ],
    "extend-exclude": [],
}

ALL_COMMANDS = {
    "pyupgrade": {"type": "formatter"},
    "isort": {"type": "formatter"},
    "black": {"type": "formatter"},
    "pflake8": {"type": "linter"},
    "mypy": {"type": "linter"},
    "pylint": {"type": "linter"},
    "pytest": {"type": "tester"},
}

NCOLS = 128

lock = threading.Lock()
logger = logging.getLogger(__name__)


def main() -> typing.NoReturn:
    """エントリポイント。"""
    returncode = run()
    logger.debug(f"{returncode=}")
    # poetryは今のところreturnしてもそれを終了コードにはしてくれないらしい
    # https://github.com/python-poetry/poetry/issues/2369
    sys.exit(returncode)


def run(args: typing.Sequence[str] = None) -> int:
    """ツール本体。"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose", default=False, action="store_true", help="shows verbose output."
    )
    parser.add_argument(
        "--commands",
        default=",".join(ALL_COMMANDS),
        help=f'comma separated list of commands. (default: {",".join(ALL_COMMANDS)})',
    )
    parser.add_argument(
        "--generate-config",
        default=False,
        action="store_true",
        help="generate a sample configuration. (part of pyproject.toml)",
    )
    parser.add_argument(
        "targets",
        nargs="*",
        type=pathlib.Path,
        help="target files and/or directories. (default: .)",
    )
    args = parser.parse_args(args)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO, format="%(message)s"
    )
    if args.generate_config:
        logging.info(
            "[tool.pyfltr]\n"
            + "\n".join(
                f"{key} = "
                + repr(value)
                .replace("'", '"')
                .replace("True", "true")
                .replace("False", "False")
                for key, value in CONFIG.items()
            )
        )
        return 0
    # check
    commands = args.commands.split(",")
    for command in commands:
        if command not in CONFIG:
            parser.error(f"command not found: {command}")

    # pyproject.toml
    pyproject_path = pathlib.Path("pyproject.toml").absolute()
    if pyproject_path.exists():
        logger.debug(f"config: {pyproject_path}")
        pyproject_data = tomli.loads(
            pyproject_path.read_text(encoding="utf-8", errors="backslashreplace")
        )
        for key, value in pyproject_data.get("tool", {}).get("pyfltr", {}).items():
            key = key.replace("_", "-")  # 「_」区切りと「-」区切りのどちらもOK
            if key not in CONFIG:
                logger.error(f"Invalid config key: {key}")
                return 1
            if not isinstance(value, type(CONFIG[key])):  # 簡易チェック
                logger.error(
                    f"invalid config value: {key}={type(value)}"
                    f", expected {type(CONFIG[key])}"
                )
                return 1
            logger.debug(
                f"config: {key} = {repr(value)} (default: {repr(CONFIG[key])})"
            )
            CONFIG[key] = value

    # run
    results = _run_commands(commands, args)

    # summary
    logger.info(f"{'-' * 10} summary {'-' * (72 - 10 - 9)}")
    for result in results:
        logger.info(f"    {result.command:<16s} {result.get_status_text()}")
    logger.info("-" * 72)

    return 0 if all(result.returncode == 0 for result in results) else 1


def _run_commands(commands, args):
    """コマンドの実行。"""
    results: list[CommandResult] = []

    # run formatters (serial)
    for command in commands:
        if CONFIG[command] and ALL_COMMANDS[command]["type"] == "formatter":
            results.append(run_command(command, args))

    # run linters/testers (parallel)
    jobs: list[typing.Any] = []
    for command in commands:
        if CONFIG[command] and ALL_COMMANDS[command]["type"] != "formatter":
            jobs.append(joblib.delayed(run_command)(command, args))
    if len(jobs) > 0:
        with joblib.Parallel(n_jobs=len(jobs), backend="threading") as parallel:
            results.extend(parallel(jobs))

    return results


@dataclasses.dataclass
class CommandResult:
    """コマンドの実行結果。"""

    command: str
    returncode: int | None
    files: int
    elapsed: float

    def get_status_text(self):
        """文字列化。"""
        if self.returncode is None:
            status = "skipped"
        elif self.returncode == 0:
            status = "succeeded"
        elif self.command in ("pyupgrade", "isort", "black"):
            status = "formatted"
        else:
            status = "failed"
        return f"{status} ({self.files}files in {self.elapsed:.1f}s)"


def run_command(command: str, args: argparse.Namespace) -> CommandResult:
    """コマンドの実行。"""
    globs = ["*_test.py"] if command == "pytest" else ["*.py"]
    targets = _expand_globs(args.targets, globs)
    if len(targets) <= 0:
        return CommandResult(command=command, returncode=None, files=0, elapsed=0)

    commandline = [CONFIG[f"{command}-path"]]
    commandline.extend(CONFIG[f"{command}-args"])
    commandline.extend(map(str, targets))

    # black/isortは--checkしてから変更がある場合は再実行する
    check_args = ["--check"] if command in ("black", "isort") else []

    # 実行
    start_time = time.perf_counter()
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        commandline + check_args,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        text=True,
        encoding="utf-8",
        errors="backslashreplace",
    )
    returncode = proc.returncode  # --check時のreturncodeを採用
    # black/isortの再実行
    if returncode != 0 and command in ("black", "isort"):
        proc = subprocess.run(
            commandline,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            text=True,
            encoding="utf-8",
            errors="backslashreplace",
        )
    output = proc.stdout.strip()  # 再実行時の出力を採用
    elapsed = time.perf_counter() - start_time

    # 結果表示
    mark = "*" if returncode == 0 else "@"
    with lock:
        logger.info(f"{mark * 32} {command} {mark * (NCOLS - 34 - len(command))}")
        logger.debug(
            f"{mark} commandline: {' '.join(shlex.quote(a) for a in commandline)}"
        )
        logger.info(mark)
        logger.info(output)
        logger.info(mark)
        logger.info(f"{mark} returncode: {returncode}")
        logger.info(mark * NCOLS)

    return CommandResult(
        command=command, returncode=returncode, files=len(targets), elapsed=elapsed
    )


def _expand_globs(targets: list[pathlib.Path], globs: list[str]) -> list[pathlib.Path]:
    """対象ファイルのリストアップ。"""
    # 空ならカレントディレクトリを対象とする
    if len(targets) == 0:
        targets = [pathlib.Path(".")]

    expanded: list[pathlib.Path] = []

    def _expand_target(target):
        try:
            if _excluded(target):
                pass
            elif target.is_dir():
                # ディレクトリの場合、再帰
                for child in target.iterdir():
                    _expand_target(child)
            else:
                # ファイルの場合、globsのいずれかに一致するなら追加
                if any(target.match(glob) for glob in globs):
                    expanded.append(target)
        except OSError:
            logger.warning(f"I/O Error: {target}", exc_info=True)

    for target in targets:
        _expand_target(target.absolute())

    return expanded


def _excluded(path: pathlib.Path):
    """無視パターンチェック。"""
    excludes = CONFIG["exclude"] + CONFIG["extend-exclude"]
    # 対象パスに一致したらTrue
    if any(path.match(glob) for glob in excludes):
        return True
    # 親に一致してもTrue
    part = path.parent
    for _ in range(len(path.parts) - 1):
        if any(part.match(glob) for glob in excludes):
            return True
        part = part.parent
    # どれにも一致しなかったらFalse
    return False


if __name__ == "__main__":
    main()
