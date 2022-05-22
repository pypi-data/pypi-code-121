import setuptools
from pathlib import Path

setuptools.setup(
    name="clioecsv",
    version=1.4,
    description="A module to import, transform (remove top / bottom, distinct, append and merge) and export to csv",
    keywords=["csv file", "txt file"],
    long_description=Path("README.md").read_text(),
    author='Cheny Lioe',
    author_email='chenylioe@yahoo.com',
    packages=setuptools.find_packages(exclude=["tests", "data"])
)
