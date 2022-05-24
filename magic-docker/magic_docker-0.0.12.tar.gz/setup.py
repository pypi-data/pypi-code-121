#!/usr/bin/env python
from setuptools import find_packages, setup


project = "magic_docker"
version = "0.0.12"


setup(
    name=project,
    py_modules=[project],
    package_dir={".":"src"},
    version=version,
    description="Automated Docker-Image-Builder Extention for Docker",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Babak EA",
    author_email="emami.babak@gmail.com",
    url="https://github.com/BabakEA/magic_docker",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
	"stdlib_list>=0.5.0",
	"ipywidgets==7.5.1",
        "numpy>=1.18.0",
    ],
    setup_requires=[
        "nose>=1.3.7",
    ],
    extras_require={
        "test": [
            "IPython >= 7.12.0",
            "notebook >=6.0.1",
        ],
    },
)
