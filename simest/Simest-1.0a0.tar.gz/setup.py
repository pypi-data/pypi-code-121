from setuptools import setup
from simest import __version__

desc = None

with open("README.md", "r") as file:
    desc = file.read()

setup(
    name="Simest",
    description="Simest - Simple and small code testing library for Python 3.8+",
    long_description=desc,
    long_description_content_type="text/markdown",
    version=__version__,

    license="MIT",

    url="https://pikostudios.dev",
    author="cookieguy",
    author_email="mail@frankiee.me",

    py_modules=['simest'],
)