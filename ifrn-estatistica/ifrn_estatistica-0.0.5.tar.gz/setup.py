#!/usr/bin/python3

from setuptools import setup, find_packages


with open('README.md', 'rb') as f:
    readme = f.read().decode('utf-8')

with open('requirements.txt') as f:
    requires = f.readlines()

PACKAGE = "ifrn_estatistica"
NAME = "ifrn_estatistica"
DESCRIPTION = "Tabela descritiva"
AUTHOR = "Ivo Trindade"
AUTHOR_EMAIL = "haddleytrindade@gmail.com"
URL = "https://github.com/hadtrindade/ifrn-estatistica"
VERSION = "0.0.5"

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    keywords="tabela descritiva",
    url=URL,
    description=DESCRIPTION,
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Framework :: Pytest",
        "Topic :: Software Development :: Testing :: Unit",
    ],
    zip_safe=False,
)
