import sys

from setuptools import find_packages
from setuptools import setup

import relaton


def empty_or_comment(x):
    return len(x) == 0 or x.strip().startswith("#")


if sys.version_info < (3, 7):
    print(
        'relaton requires Python 3 version >= 3.7',
        file=sys.stderr)
    sys.exit(1)

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as reqs:
    requirements = filter(empty_or_comment, reqs.read().splitlines())

with open('requirements_dev.txt') as reqs:
    dev_requirements = filter(empty_or_comment, reqs.read().splitlines())



desc = (
    "Library for working with Relaton bibliographic data models in Python. "
    "Provides Pydantic models and dataclasses, "
    "as well as parsers and serializers.")

version = relaton.__version__

setup(
    name='relaton',
    version=version,
    description=desc,
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Ribose Inc.',
    url='http://github.com/relaton/relaton-py/',
    author_email='open@ribose.com',
    license='BSD 2-clause',
    include_package_data=True,
    install_requires=requirements,
    tests_require=dev_requirements,
    packages=find_packages(include=['relaton', 'relaton.*']),
    zip_safe=False,
    keywords=[
        'Relaton',
        'bibliographic data',
        'bibliography',
        'Pydantic',
        'dataclasses',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
    ],
)
