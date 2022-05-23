import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="gradesucope",
    version="1.2.0",
    description="Libraries that make it easier to write nice Gradescope autograders at UC.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/hawkinsw/gradesucope",
    author="Will Hawkins",
    author_email="whh8b@obs.cr",
    license="GPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["gradescope-utils", "subprocess32"],
)
