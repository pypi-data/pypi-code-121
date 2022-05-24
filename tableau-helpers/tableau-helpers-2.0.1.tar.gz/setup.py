import io
import os
import re

from setuptools import find_packages, setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type("")
    with io.open(filename, mode="r", encoding="utf-8") as fd:
        return re.sub(text_type(r":[a-z]+:`~?(.*?)`"), text_type(r"``\1``"), fd.read())


setup(
    name="tableau-helpers",
    version="2.0.1",
    url="https://bitbucket.rki.local/projects/MF4/repos/tableau_helpers",
    license="MIT",
    author="Kyle Krueger",
    author_email="kyle.s.krueger@gmail.com",
    description="A collection of helpers to reduce boilerplate with Tableau APIs.",
    long_description=read("README.md"),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "tableauhyperapi>=0.0.14109",
        "tableauserverclient>=0.17.0",
        "python-dotenv",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
