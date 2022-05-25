import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="fuse_cdm",
    version="1.5.0",
    description="Access fuse common data model library for cellfie analysis suite",
    long_description=README,
    long_description_content_type="text/markdown",
    url=" ",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    # install_requires=[],
    # entry_points={
    #     "console_scripts": [
    #
    #     ]
    # },
)