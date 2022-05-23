import fire

from tdf_tools.pipeline import Pipeline
from ruamel import yaml

from tdf_tools.tools.print import Print


def main():
    dirInvalidate()
    fire.Fire(Pipeline())


# 目录校验，确保只能在壳下执行tdf_tools
def dirInvalidate():
    with open("pubspec.yaml", encoding="utf-8") as f:
        doc = yaml.round_trip_load(f)
        if isinstance(doc, dict) and doc.__contains__("flutter"):
            if (
                isinstance(doc["flutter"], dict)
                and doc["flutter"].__contains__("module") is not True
            ):
                Print.error("当前不是壳工程目录，禁止执行tdf_tools命令")
        f.close()
