from glob import glob

import setuptools.command.build_ext

from pybind11.setup_helpers import build_ext, Pybind11Extension
from setuptools import Extension, setup

setup(
    name="pyderevo",
    version="0.0.8",
    author="Ivan Kobzarev",
    author_email="ivan.kobzarev@gmail.com",
    description="Containers manipulation library",
    url="https://github.com/IvanKobzarev/pytree",
    ext_modules=[
        Pybind11Extension(
            name="pytree",
            sources=["pytree/csrc/pytree_bindings.cpp"],
            include_dirs=["include"],
        )
    ],
    setup_requires=["pybind11"],
    install_requires=["pybind11"],
    cmdclass={
        "build_ext": build_ext,
    },
)
