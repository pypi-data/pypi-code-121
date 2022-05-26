from setuptools import find_packages, setup

# Package meta-data.
NAME = 'yue'
DESCRIPTION = 'A daily useful kit by KIN.'
URL = 'https://github.com/githubuser/kin.git'
EMAIL = 'emailuser@foxmail.com'
AUTHOR = 'KIN'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.0.1001'

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
    license="MIT"
)