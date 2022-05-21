import os
from os.path import join, dirname


def load_script(filename):
    expected_script = join(dirname(__file__), "scripts", filename)
    with open(expected_script, "rt") as fd:
        return fd.read()


def launch_folder(name: str):
    os.chdir(os.path.join(os.path.dirname(__file__), 'assets', name))

