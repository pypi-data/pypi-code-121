from numpy import source
from setuptools import setup, find_packages

setup(
    name='YTRequests',
    author="tsubasa652",
    author_email="mail@tsubasa.ml",
    maintaner="tsubasa652",
    maintainer_email="mail@tsubasa.ml",
    url="https://github.com/tsubasa652/python-YTRequests",
    download_url="https://github.com/tsubasa652/python-YTRequests",
    version='1.0.2',
    packages=find_packages(),
    install_requires=["requests"],
    license="MIT",
    source="https://github.com/tsubasa652/python-YTRequests"
)