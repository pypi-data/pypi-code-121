from setuptools import find_packages, setup

# Package meta-data.
import wu

NAME = '000'
DESCRIPTION = 'A daily useful kit by WU.'
URL = 'https://github.com/username/wu.git'
EMAIL = 'wu@foxmail.com'
AUTHOR = 'WU'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = wu.VERSION

# What packages are required for this module to be executed?
REQUIRED = []

# Setting.
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(),
    install_requires=REQUIRED,
    license="MIT",
    platforms=["all"],
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type="text/markdown"
)