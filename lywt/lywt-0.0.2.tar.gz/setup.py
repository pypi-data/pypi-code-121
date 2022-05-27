from setuptools import find_packages, setup

# Package meta-data.
NAME = 'lywt'
DESCRIPTION = 'laolu的工具包'
URL = 'https://github.com/LuShengcan'
AUTHOR_EMAIL = 'shengcan_lu@foxmail.com'
AUTHOR = 'laolu'
REQUIRES_PYTHON = '>=3.0'
VERSION = '0.0.2'

# What packages are required for this module to be executed?
REQUIRED = ['requests', 'bs4', 'lxml']

# Setting.
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(),
    install_requires=REQUIRED,
    license="MIT"
)

# 打包命令
# python setup.py sdist build
# twine upload dist/*
