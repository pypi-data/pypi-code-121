import setuptools
from pathlib import Path

setuptools.setup(
    name="timopdf",
    version=2.0,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["tests", "data"])
)
