#!/usr/bin/env python

import os
import sys

from setuptools import Distribution, Extension, find_packages, setup

required = [
    "numpy",
    "scipy",
    "recfast4py>=0.2.4",
    "dill",
    "matplotlib",
    "numba",
    "sympy2c>=1.0.4",
]


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        # file might not exist when package is installed as dependency:
        return ""


class BinaryDistribution(Distribution):

    """as this setup.py does not declare c code to compile, 'setup.py bdist_wheel'
    would create source wheels, unless we implement this 'fake' class and use
    it as 'distclass=BinaryDistribution' below.
    """

    def has_ext_modules(self):
        return True


def create_ext_modules():
    """
    Build commands require preinstalled numpy to compile the c extensions. A
    global "import numpy" here would break tox and also if installed as a
    dependency from another python package. So we only require numpy for the
    cases where its header files are actually needed.
    """

    build_commands = (
        "build",
        "build_ext",
        "build_py",
        "build_clib",
        "build_scripts",
        "bdist_wheel",
        "bdist_rpm",
        "bdist_wininst",
        "bdist_msi",
        "bdist_mpkg",
        "build_sphinx",
        "develop",
        "install",
        "install_lib",
        "install_header",
    )

    ext_modules = []
    if any(command in build_commands for command in sys.argv[1:]):
        try:
            import numpy
        except ImportError:
            raise Exception(
                "please install numpy, need numpy header files to compile c extensions"
            )

        from Cython.Build import cythonize

        cythonize("PyCosmo/cython/halo_integral.pyx")
        files = [
            "const.c",
            "main.c",
            "halo_integral.c",
            "polevl.c",
            "sici.c",
            "sicif.c",
            "polevlf.c",
            "logf.c",
            "sinf.c",
            "constf.c",
            "mtherr.c",
        ]
        ext_modules = [
            Extension(
                "PyCosmo.cython.halo_integral",
                sources=["PyCosmo/cython/" + file for file in files],
                include_dirs=[numpy.get_include()],
            )
        ]
    return ext_modules


setup(
    name="PyCosmo",
    version="2.0.3",  # no need to update version in other places of PyCosmo
    author="Institute for Cosmology",
    author_email="pycosmo@lists.phys.ethz.ch",
    url="https://cosmo-docs.phys.ethz.ch/PyCosmo",
    license="GPLv3",
    packages=find_packages(where=".", exclude=["examples", "tests"]),
    description="A multi-purpose cosmology calculation tool",
    long_description=read("README.rst"),
    install_requires=required,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: C",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points="""
        [console_scripts]
        recompile=PyCosmo:Cosmo.recompile_from_cli
    """,
    distclass=BinaryDistribution,
    ext_modules=create_ext_modules(),
)
