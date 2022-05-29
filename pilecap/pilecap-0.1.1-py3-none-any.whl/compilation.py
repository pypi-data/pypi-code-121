import os
import pathlib
import re
import subprocess
from typing import Dict, Optional, Sequence, Set

from pilecap import gathering

PRIVATE_CONSTRAINTS = "constraints.txt"
_SHARED_CONSTRAINTS = "constraints/shared.txt"
_DEV_REQUIREMENTS = "requirements/dev.txt"


def _shared_constraints(project_dir: pathlib.Path) -> Set[str]:
    return set((project_dir / _SHARED_CONSTRAINTS).read_text().splitlines())


def _run_requirements(project_dir: pathlib.Path) -> Set[str]:
    return gathering.run_requirements(project_dir)


def _dev_requirements(project_dir: pathlib.Path) -> Set[str]:
    from_build = gathering.build_dependencies(project_dir)
    from_dev = set((project_dir / _DEV_REQUIREMENTS).read_text().splitlines())
    return from_build | from_dev


def _pip_compile(
    wdir: pathlib.Path,
    requirements: Sequence[pathlib.Path],
    hard_constraints: Sequence[pathlib.Path],
    soft_constraints: Sequence[pathlib.Path],
    stem: str,
    strip_extras: bool = False,
    custom_compile_command: Optional[str] = None,
) -> pathlib.Path:
    # pylint: disable=too-many-arguments
    src = wdir / f"{stem}.in"
    dst = wdir / f"{stem}.txt"

    with src.open("x") as f:
        for r in requirements:
            f.write(f"-r {r}\n")
        for c in hard_constraints:
            f.write(f"-c {c}\n")

    with dst.open("x") as f:
        for c in soft_constraints:
            f.write(c.read_text())

    extra_env = {}
    if custom_compile_command is not None:
        extra_env["CUSTOM_COMPILE_COMMAND"] = custom_compile_command

    cmd = ["pip-compile", "--allow-unsafe", "--quiet", "--output-file", os.fspath(dst)]
    if strip_extras:
        cmd.append("--strip-extras")
    cmd.append(os.fspath(src))
    subprocess.check_call(cmd, env=os.environ | extra_env)

    return dst


def _intersection(keys_from: str, versions_from: str) -> Dict[str, str]:
    prog = re.compile(r"^\s*(?P<name>\S+)==(?P<version>\S+)\s*$", flags=re.MULTILINE)
    names = set(match.group("name") for match in prog.finditer(keys_from))
    versions = {
        match.group("name"): match.group("version")
        for match in prog.finditer(versions_from)
    }
    return {k: v for k, v in versions.items() if k in names}


def _pretty(wdir: pathlib.Path, text: str) -> str:
    return re.sub(
        f"-(?P<flag>[cr]) {wdir}/(?P<name>.+)\\.(in|txt)",
        "-\\g<flag> \\g<name>",
        text,
        flags=re.MULTILINE,
    )


def private_constraints(wdir: pathlib.Path, project_root: pathlib.Path) -> str:
    old_constraints_txt = project_root / PRIVATE_CONSTRAINTS
    dev_requirements_in = wdir / "dev.in"
    run_requirements_in = wdir / "run.in"

    with run_requirements_in.open("x") as f:
        for r in _run_requirements(project_root):
            f.write(f"{r}\n")

    with dev_requirements_in.open("x") as f:
        for r in _dev_requirements(project_root):
            f.write(f"{r}\n")

    all_shared_constraints_txt = _pip_compile(
        wdir=wdir,
        requirements=[run_requirements_in],
        hard_constraints=[project_root / _SHARED_CONSTRAINTS],
        # The soft constraints here should not affect the final result, but
        # I think they may improve speed.
        soft_constraints=[old_constraints_txt] if old_constraints_txt.exists() else [],
        stem="all_shared",
        strip_extras=False,
    )

    # Prevent unconstrained packages from misleadingly being annotated with
    # "via -c shared".
    shared_constraints_txt = wdir / "shared.txt"
    with shared_constraints_txt.open("x") as f:
        items = _intersection(
            (project_root / _SHARED_CONSTRAINTS).read_text(),
            all_shared_constraints_txt.read_text(),
        ).items()
        for name, version in sorted(items):
            f.write(f"{name}=={version}\n")

    new_constraints_txt = _pip_compile(
        wdir=wdir,
        requirements=[run_requirements_in, dev_requirements_in],
        hard_constraints=[shared_constraints_txt],
        soft_constraints=[old_constraints_txt] if old_constraints_txt.exists() else [],
        stem="private",
        strip_extras=True,
        custom_compile_command="pilecap compile",
    )

    return _pretty(wdir, new_constraints_txt.read_text())
