from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read().replace("\r\n", "\n")

requires = [
    "pandas>=0.22",
]

requires_dev = requires + [
    "black>=20.",
    "bump2version>=1.0.0",
    "check-manifest",
    "flake8>=3.7.8",
    "flake8-black>=0.2.1",
    "pytest>=4.3.0",
    "pytest-cov>=2.6.1",
]

setup(
    name="finance_enums",
    version="0.1.1",
    description="Standard Finance enums",
    long_description=long_description,
    url="https://github.com/timkpaine/finance_enums",
    download_url="https://github.com/timkpaine/finance_enums/archive/v0.1.0.tar.gz",
    author="Tim Paine",
    author_email="t.paine154@gmail.com",
    license="Apache 2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="finance data",
    packages=find_packages(exclude=[]),
    include_package_data=True,
    install_requires=requires,
    extras_require={"dev": requires_dev},
)
