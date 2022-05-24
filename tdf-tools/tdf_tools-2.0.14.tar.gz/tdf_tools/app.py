import fire

from tdf_tools.pipeline import Pipeline
from ruamel import yaml

from tdf_tools.tools.print import Print


def main():
    fire.Fire(Pipeline())
