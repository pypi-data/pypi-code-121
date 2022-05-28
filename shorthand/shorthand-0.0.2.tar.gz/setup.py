import setuptools
from setuptools import setup


NAME = 'shorthand'
VERSION = '0.0.2'
URL = 'https://github.com/SSripilaipong/shorthand'
LICENSE = 'MIT'
AUTHOR = 'SSripilaipong'
EMAIL = 'SHSnail@mail.com'

setup(
    name=NAME,
    version=VERSION,
    packages=[p for p in setuptools.find_packages() if p.startswith(f"{NAME}.") or p == NAME],
    url=URL,
    license=LICENSE,
    author=AUTHOR,
    author_email=EMAIL,
    description=None,
    long_description=None,
    python_requires='>=3.6',
    install_requires=[],
    classifiers=[],
    include_package_data=True,
)

