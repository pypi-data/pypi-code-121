from __future__ import annotations

import argparse
import contextlib
import datetime
import os
import pathlib
import subprocess
import tempfile
from typing import Iterator, List

from pilecap import compilation, gathering


def _flag_from_environ(name: str) -> bool:
    lut = {
        "1": True,
        "0": False,
        None: False,
    }
    return lut[os.environ.get(f"PILECAP_{name}")]


@contextlib.contextmanager
def _tmpdir() -> Iterator[pathlib.Path]:
    if _flag_from_environ("DEBUG"):
        yield pathlib.Path(
            tempfile.mkdtemp(
                prefix=datetime.datetime.now().strftime("tmp_%Y%m%d_%H%M%S"),
                dir=pathlib.Path.cwd(),
            )
        )
        return
    with tempfile.TemporaryDirectory() as wdir:
        yield pathlib.Path(wdir)


def _project_root() -> pathlib.Path:
    """Return project root if it can be guessed"""
    result = pathlib.Path.cwd()
    pyproject_toml = result / "pyproject.toml"
    assert pyproject_toml.exists()
    return result


def _install(args: argparse.Namespace) -> None:
    extra_env = {"PIP_CONSTRAINT": "constraints.txt"}
    subprocess.check_call(
        ["pip", "install"] + args.args,
        env=os.environ | extra_env,
    )


def _update(_: argparse.Namespace) -> None:
    project_root = _project_root()
    with _tmpdir() as wdir:
        after = compilation.private_constraints(pathlib.Path(wdir), project_root)
    (project_root / compilation.PRIVATE_CONSTRAINTS).write_text(after)


def _build_requirements(args: argparse.Namespace) -> None:
    for dep in sorted(gathering.build_dependencies(args.project_root)):
        print(dep)


def _run_requirements(args: argparse.Namespace) -> None:
    for dep in sorted(gathering.run_requirements(args.project_root)):
        print(dep)


def _parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    submain = result.add_subparsers(required=True)

    install_ = submain.add_parser(
        "install",
        help="Install package using pip, see that program for all options",
    )
    install_.add_argument("args", nargs="*")
    install_.set_defaults(func=_install)

    update = submain.add_parser(
        "update",
        help="Update constraints.txt",
    )
    update.set_defaults(func=_update)

    plumbing = submain.add_parser(
        "plumbing",
        help="Access to low level functions",
    )
    subplumbing = plumbing.add_subparsers()
    breqs = subplumbing.add_parser(
        "build-requirements",
        help="Print all immediate dependencies for building the package",
    )
    breqs.add_argument("project_root", type=pathlib.Path)
    breqs.set_defaults(func=_build_requirements)
    rreqs = subplumbing.add_parser(
        "run-requirements",
        help="Print all immediate dependencies for running the package",
    )
    rreqs.add_argument("project_root", type=pathlib.Path)
    rreqs.set_defaults(func=_run_requirements)

    return result


def cli(args: List[str]) -> None:
    parsed = _parser().parse_args(args)
    parsed.func(parsed)
