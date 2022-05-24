import os
from workspace import env, git, message, cmake

name = "install"
help = """Installs a module given its name"""
usage = "[repository [repository [...]]]"
min_args = 0


def run(args):
    for repository in args:
        if not git.install(repository, "user"):
            message.error("Not installing " + repository + " because the directory already exists")
    git.scan_all_dependencies()
    cmake.generate()
