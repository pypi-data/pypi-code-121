"""
New setup file for PyPI, package of zeno_etl_lib
"""

import pathlib

from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text(encoding='utf-8')

setup(
    name="zeno_etl_libs",
    version="1.0.31",
    description="Zeno ETL Custom library",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/workcell/etl/src/master/",
    author="Zeno ETL Team",
    author_email="data@zeno.health",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(exclude=("tests", "ci-cd", "db-migrations", "etl_libs", "glue-jobs", "secret",
                                    "extra_dependency")),
    # packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "zeno_etl_libs=zeno_etl_libs.__main__:main",
        ]
    },

)