"""The setup script."""

from setuptools import setup, find_packages
from pathlib import Path
import os


# Package meta-data.
NAME = 'TweetsAnalysis'
DESCRIPTION = "Real Time Tweets Analysis."
URL = 'https://github.com/HassanRady/TweetAnalysis'
EMAIL = 'hassan.khaled.rady@gmail.com'
AUTHOR = "Hassan Rady"
REQUIRES_PYTHON = ">=3.6.0"

# Load the package's VERSION file as a dictionary.
about = {}
ROOT_DIR = Path(__file__).resolve().parent
REQUIREMENTS = ROOT_DIR/ 'requirements.txt'
PACKAGE_DIR = ROOT_DIR / 'TweetAnalysis'

with open(PACKAGE_DIR / "VERSION") as f:
    _version = f.read().strip()
    about["__version__"] = _version

# Long description
with open('README.md') as readme_file:
    readme = readme_file.read()


# What packages are required for this module to be executed?
def list_reqs():
    with open(REQUIREMENTS) as fd:
        return fd.read().splitlines()

test_requirements = ['pytest>=3', ]

setup(
    author=AUTHOR,
    author_email=EMAIL,
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description_content_type='text/markdown',
    long_description=readme,
    url=URL,
    python_requires=REQUIRES_PYTHON,
    install_requires=list_reqs(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    license="MIT license",
    include_package_data=True,
    keywords='Tweets',
    packages=find_packages(include=['TweetAnalysis', 'TweetAnalysis.*']),
    test_suite='tests',
    tests_require=test_requirements,
    zip_safe=False,
)
