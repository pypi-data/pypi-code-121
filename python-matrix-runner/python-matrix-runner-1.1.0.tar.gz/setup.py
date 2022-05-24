# -*- coding: utf-8 -*-

import re
import subprocess

from setuptools import setup


def version_from_git_tag():
    """Retrieve version from git history."""
    # Using package version according to PEP 440 -- Version Identification and Dependency Specification
    # https://www.python.org/dev/peps/pep-0440/#local-version-identifiers
    pattern = "^v((\\d+)\\.(\\d+)\\.(\\d+)((a|b|rc)\\d+)?(\\.post\\d+)?(\\.dev\\d+)?)(-(\\d+)-g([0-9a-f]{7}))?$"
    try:
        describe = subprocess.check_output(["git", "describe", "--tags", "--match", "v*", "--always"]).rstrip().decode()
    except subprocess.CalledProcessError:
        return "0.0.0+nogit"

    match = re.match(pattern, describe)
    if not match:
        return f"0.0.0+git{describe}"
    if match.group(10) and match.group(11):
        return f"{match.group(1)}+git{match.group(10)}.{match.group(11)}"
    return match.group(1)


setup(
    name='python-matrix-runner',
    version=version_from_git_tag(),
    packages=['matrix_runner'],
    install_requires=[
        'allpairspy~=2.5',
        'ansicolors~=1.1',
        'colorama~=0.4',
        'colorlog~=6.6',
        'filelock~=3.4',
        'junitparser~=2.2',
        'lxml~=4.6',
        'parameterized~=0.8',
        'psutil~=5.8',
        'tabulate~=0.8'
    ],
    extras_require={
        'dev': [
            'coverage~=6.2',
            'pylint~=2.11',
            'restructuredtext_lint~=1.3',
            'setuptools~=59.4',
            'unittest-xml-reporting~=3.0'
        ]
    },
    entry_points={
        'console_scripts': ['matrix-runner-inspect=matrix_runner.inspect:InspectRunner'],
    },
    python_requires='>=3.8',
    url='https://github.com/energy6/python-matrix-runner',
    license='BSD 3-Clause License',
    author='Jonatan Antoni',
    author_email='jonatan@familie-antoni.de',
    description='Helper to run command with matrix configurations',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Build Tools"
    ]
)
