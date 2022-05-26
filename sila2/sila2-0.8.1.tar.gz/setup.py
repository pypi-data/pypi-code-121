# this file only deals with dynamic setup (e.g. copying files from sila_base),
# the static setup is done in pyproject.toml
from distutils.dir_util import copy_tree
from glob import glob
from os import makedirs
from os.path import basename, dirname, join
from shutil import copy

from setuptools import setup

base_dir = dirname(__file__)


def create_dir_with_init_file(path: str) -> None:
    makedirs(path, exist_ok=True)
    with open(join(path, "__init__.py"), "w", encoding="utf-8"):
        pass


def copy_resources_from_sila_base() -> None:
    resource_dir = join(base_dir, "src", "sila2", "resources")
    makedirs(resource_dir, exist_ok=True)

    # xsd
    xsd_dir = join(resource_dir, "xsd")
    create_dir_with_init_file(xsd_dir)
    copy_tree(join(base_dir, "sila_base", "schema"), xsd_dir)

    # xsl
    xsl_dir = join(resource_dir, "xsl")
    create_dir_with_init_file(xsl_dir)
    for file in glob(join(base_dir, "sila_base", "xslt", "*.xsl")):
        copy(file, join(xsl_dir, basename(file)))

    # proto
    proto_dir = join(resource_dir, "proto")
    create_dir_with_init_file(proto_dir)
    copy(
        join(base_dir, "sila_base", "protobuf", "SiLAFramework.proto"),
        join(proto_dir, "SiLAFramework.proto"),
    )
    copy(
        join(base_dir, "sila_base", "protobuf", "SiLABinaryTransfer.proto"),
        join(proto_dir, "SiLABinaryTransfer.proto"),
    )


copy_resources_from_sila_base()
setup()
