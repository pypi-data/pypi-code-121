from setuptools import find_packages, setup

from nbresnote import __version__

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="nbresnote",
    version = __version__,
    py_modules=["nbresnote"],
    author="jhjung",
    author_email="jhjung@uos.ac.kr",
    description="auto research note conversion",
    scripts=['bin/nbresnote'],
    long_description=long_description
    #url="https://yheom.sscc.uos.ac.kr/gitlab/csns-lab/auto-research-note"
)