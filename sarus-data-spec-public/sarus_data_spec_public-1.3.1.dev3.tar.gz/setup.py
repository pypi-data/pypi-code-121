#!/usr/bin/env python
from subprocess import check_call
import pathlib

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop


def generate_proto_code():
    proto_path = "sarus_data_spec/protobuf"
    proto_it = pathlib.Path().glob(proto_path + "/**/*.proto")
    protos = [str(proto) for proto in proto_it if proto.is_file()]
    check_call(
        [
            "protoc",
            "--python_out",
            ".",
            "--mypy_out",
            ".",
            "--proto_path",
            ".",
        ]
        + protos
    )


class CompileProtobufDevelop(develop):
    """Wrapper to add protobuf compilation to run before editable package installation."""

    uninstall = False

    def run(self):
        develop.run(self)

    def install_for_development(self):
        develop.install_for_development(self)
        generate_proto_code()


class CompileProtobufBuild(build_py):
    """Wrapper to add protobuf compilation to run before package installation."""

    def run(self):
        generate_proto_code()
        build_py.run(self)


if __name__ == '__main__':
    setup(version='1.3.1.dev3')
