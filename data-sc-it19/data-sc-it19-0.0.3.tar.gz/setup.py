from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.3'
DESCRIPTION = ''

# Setting up
setup(
    name="data-sc-it19",
    version=VERSION,
    author="unknown",
    author_email="",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy', 'matplotlib', 'pandas'],
    keywords=['data'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
