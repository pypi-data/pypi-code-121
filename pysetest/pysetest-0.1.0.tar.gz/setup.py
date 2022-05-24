import pathlib

from setuptools import setup

HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="pysetest",
    version="0.1.0",
    description="E2E ",
    packages=["pyse"],
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/titanom/pysetest",
    author="uhasker",
    author_email="uhasker@protonmail.com",
    license="MIT",
    install_requires=["requests"]
)
