import os
from workspace import env, git, message, cmake

name = "cmake"
help = """(Re-)Generates the meta cmake"""
usage = ""
min_args = 0


def run(args):
    cmake.generate()
