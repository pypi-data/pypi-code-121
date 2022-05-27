from setuptools import setup
from simest import __version__

desc = None

with open("README.md", "r") as file:
    desc = file.read()

setup(
    name="Simest",
    description=desc,
    version=__version__,

    license="MIT",

    url="https://pikostudios.dev",
    author="cookieguy",
    author_email="mail@frankiee.me",

    py_modules=['simest']
)