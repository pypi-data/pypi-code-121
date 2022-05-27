#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
from pathlib import Path

import pytoml


def filter_packages(data):
    return {
        key for key, value in data.items() if key != "python" and isinstance(value, str)
    }


def update_packages(packages, project_root, dev=False):
    if packages:
        packages = ["{p}@latest".format(p=p) for p in packages]
        command = ["poetry", "add"] + packages
        if dev:
            command += ["--dev"]
        command += ["-vvv"]
        subprocess.run(command, cwd=project_root, check=True)


def main():
    project_root = Path(sys.argv[1]).expanduser().absolute()
    with open(project_root / "pyproject.toml") as f:
        data = pytoml.load(f)

    packages = filter_packages(data["tool"]["poetry"].get("dependencies", []))
    dev_packages = filter_packages(data["tool"]["poetry"].get("dev-dependencies", []))

    update_packages(packages, project_root, dev=False)
    update_packages(dev_packages, project_root, dev=True)


if __name__ == "__main__":
    main()
