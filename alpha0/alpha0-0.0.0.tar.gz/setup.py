from setuptools import find_packages, setup

# Package meta-data.
import yue

NAME = 'alpha0'
DESCRIPTION = 'A daily useful kit by KIN.'
URL = 'https://github.com/githubuser/kin.git'
EMAIL = 'emailuser@foxmail.com'
AUTHOR = 'KIN'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = yue.VERSION

# What packages are required for this module to be executed?
REQUIRED = ['urllib3']

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