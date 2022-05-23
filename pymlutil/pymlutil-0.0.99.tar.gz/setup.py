import os, sys
import shutil
import yaml
from setuptools import setup, find_packages
from pymlutil.version import config, VersionString

version_str = VersionString(config)

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Setting up
setup(
    # the name must match the folder name 'pymlutil'
    name="pymlutil", 
    version=version_str,
    author="Brad Larson",
    author_email="<bhlarson@gmail.com>",
    description=config['description'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude="tests"),
    install_requires=['pyyaml', 'prettytable', 'minio', 'numpy', 'opencv-python', 'torch', 'scikit-learn'], # add any additional packages that 
    url = 'https://github.com/bhlarson/pymlutil',
    keywords=['python', 'Machine Learning', 'Utilities'],
    include_package_data=True,
    package_data = {'pymlutil': ['*.yaml']},
    classifiers= [
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ]
)