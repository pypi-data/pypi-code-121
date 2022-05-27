# -*- coding: utf-8 -*-

import argparse
import logging
import os
import re
import subprocess

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--project", type=str, required=True)
    parser.add_argument("--fix-torch", nargs="*", type=str)
    parser.add_argument("--cuda", type=str)

    args = parser.parse_args()  # pylint: disable=redefined-outer-name
    if args.fix_torch and not args.cuda:
        raise ValueError("`--cuda` is required if `--fix-torch` is passed")

    return args


def poetry_export(project_root, requirements_file=None):
    if not requirements_file:
        requirements_file = os.path.join(project_root, "requirements.txt")

    commands = [
        "poetry",
        "export",
        "-f",
        "requirements.txt",
        "--without-hashes",
    ]
    with open(requirements_file, mode="w", encoding="utf8") as f:
        subprocess.run(commands, cwd=project_root, stdout=f, check=True)

    return requirements_file


def fix_torch_cuda(requirements_file, package, cuda):
    def _fix(package, requirements):
        i = 0
        while not re.match(rf"^{package}[><!=]", requirements[i]):
            i += 1

        if i >= len(requirements):
            raise RuntimeError(f"{package} version not found in {requirements_file}")

        comps = requirements[i].split(";")
        if len(comps) == 1:
            comps[0] = comps[0].rstrip()

        comps[0] = (
            comps[0] + f" --extra-index-url https://download.pytorch.org/whl/{cuda}"
        )

        if len(comps) == 1:
            comps[0] += "\n"

        requirements[i] = ";".join(comps)

        return requirements

    with open(requirements_file, encoding="utf8") as f:
        requirements = list(f)

    requirements = _fix(package, requirements)

    with open(requirements_file, mode="w", encoding="utf8") as f:
        f.writelines(requirements)


def main():
    logging.basicConfig(level=logging.INFO, force=True)
    args = parse_args()

    requirement_file = poetry_export(args.project)
    for package in args.fix_torch:
        logger.info("Fixing %s version", package)
        fix_torch_cuda(requirement_file, package, args.cuda)

    logger.info("Dependencies export to %s", requirement_file)


if __name__ == "__main__":
    main()
