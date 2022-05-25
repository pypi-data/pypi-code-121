import os
import sys
from setuptools import setup


with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()


def get_packages():
    # setuptools can't do the job :(
    packages = []
    for root, dirnames, filenames in os.walk('lettuce'):
        if '__init__.py' in filenames:
            packages.append(".".join(os.path.split(root)).strip("."))

    return packages


required_modules = ['sure', 'fuzzywuzzy', 'python-subunit']


if os.name.lower() == 'nt':
    required_modules.append('colorama')

setup(
    name='lettuce_Dtester',
    version='0.2.31',
    description='Behaviour Driven Development for python',
    author='Gabriel Falcao',
    author_email='gabriel@nacaolivre.org',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://lettuce.it',
    packages=get_packages(),
    install_requires=required_modules,
    entry_points={
        'console_scripts': ['lettuce = lettuce.bin:main'],
        },
    package_data={
        'lettuce': ['COPYING', '*.md'],
    },
)
