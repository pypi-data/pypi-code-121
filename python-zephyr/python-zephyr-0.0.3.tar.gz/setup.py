import os

from setuptools import find_packages
from setuptools import setup


HERE = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

packages = find_packages(".")

setup(
    name="python-zephyr",
    version="0.0.3",
    description="An easy to use Zephyr Scale library for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=list(filter(os.path.isfile, (os.path.join("scripts/", f) for f in os.listdir("scripts/")))),
    author="Atabey Onur",
    author_email="a.onur@munichelectrification.com",
    maintainer="Atabey Onur",
    maintainer_email="a.onur@munichelectrification.com",
    url="https://bitbucket.org/melectrification/python-zephyr/src/master/",
    packages=packages,
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
