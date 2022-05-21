from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.0.0'
DESCRIPTION = 'CRUD API Generator for django'
LONG_DESCRIPTION = 'A package that allows to automatically create crud api for all manually created django apps.'

# Setting up
setup(
    name="drf-crud-generator",
    version=VERSION,
    author="Sulav Panthi",
    author_email="<panthisulav4@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['python', 'django', 'djangorestframework'],
    keywords=['python', 'drf', 'crud api', 'crud generator', 'drf crud generator'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)