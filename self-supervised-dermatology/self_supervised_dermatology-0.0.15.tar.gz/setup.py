import re
import os.path
import codecs

from setuptools import setup, find_packages
from os.path import abspath, dirname, join


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def parse_requirements(filename):
    """
    load requirements from a pip requirements file
    """
    line_iter = (line.strip() for line in open(filename))
    return [line for line in line_iter if line and not line.startswith("#")]


README_MD = open(join(dirname(abspath(__file__)), "README.md")).read()
PACKAGE_NAME = 'self_supervised_dermatology'
SOURCE_DIRECTORY = 'src'
SOURCE_PACKAGE_REGEX = re.compile(rf'^{SOURCE_DIRECTORY}')

source_packages = find_packages(
    include=[SOURCE_DIRECTORY, f'{SOURCE_DIRECTORY}.*'])
proj_packages = [
    SOURCE_PACKAGE_REGEX.sub(PACKAGE_NAME, name) for name in source_packages
]

setup(
    name=PACKAGE_NAME,
    packages=proj_packages,
    package_dir={PACKAGE_NAME: SOURCE_DIRECTORY},
    version='0.0.15',
    author='Fabian Groeger',
    author_email='fabian.groeger@hslu.ch',
    description=
    'Unsupervised Pre-Training for Texture Segmentation in Dermatology',
    long_description=README_MD,
    long_description_content_type="text/markdown",
    url='https://github.com/FabianGroeger96/',
    python_requires='>=3.6',
    install_requires=parse_requirements('requirements.pkg.txt'),
    setup_requires=parse_requirements('requirements.pkg.txt'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ])
