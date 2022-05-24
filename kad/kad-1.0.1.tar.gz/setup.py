from setuptools import setup, find_packages
import os

VERSION = '1.0.1'
DESCRIPTION = 'Use dictionary keys as attributes'
LONG_DESCRIPTION = 'A package that allows dictionaries to be used with dots rather than keys'

setup(
    name='kad',
    version=VERSION,
    author='Robin Chapple',
    author_email='r.chapple.business@gmail.com',
    description=DESCRIPTION,
    long_description_content_type='text/markdown',
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'dictionary', 'easeofuse', 'ctx', 'objects'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        ]
    )
