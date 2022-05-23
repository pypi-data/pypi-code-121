from setuptools import find_packages, setup

from nbresnote import __version__

setup(
    name="nbresnote",
    version = __version__,
    py_modules=["nbresnote"],
    author="jhjung",
    author_email="jhjung@uos.ac.kr",
    description="auto research note conversion",
    scripts=['bin/nbresnote'],
    #url="https://yheom.sscc.uos.ac.kr/gitlab/csns-lab/auto-research-note"
)