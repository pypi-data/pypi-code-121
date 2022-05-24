import os
import numpy as np
from workspace import env, git, message, cmake

name = "cmd"
help = """Run a command in all dependencies"""
usage = "[command]"
min_args = 1


def run(args):
    command = " ".join(args)
    for directory in git.get_directories():
        message.bright("* Running command in %s" % directory)
        os.system("cd %s; %s" % (directory, command))
