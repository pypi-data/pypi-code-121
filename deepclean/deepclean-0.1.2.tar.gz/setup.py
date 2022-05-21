# noqa: D100
from setuptools import find_packages, setup

import deepclean

with open("README.rst", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name="deepclean",
    version=deepclean.__version__,
    description=deepclean.__doc__.splitlines()[0],
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://git.shore.co.il/nimrod/deepclean",
    author="Nimrod Adar",
    author_email="nimrod@shore.co.il",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    keywords=[
        "docker",
    ],
    packages=find_packages(),
    install_requires=[
        "docker",
    ],
    entry_points={"console_scripts": ["deepclean=deepclean.__main__:main"]},
)
