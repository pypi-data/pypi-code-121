import pathlib

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="ingestor-module",
    version="1.14.0",
    description="Wrapper for ingestor module",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://mnc-repo.mncdigital.com/ai-team/vision_plus/rce_ingestor_module",
    author="AI Teams",
    author_email="ferdina.kusumah@mncgroup.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "graphdb-module",
        "numpy~=1.22.1",
        "pandas==1.4.0",
        "boto3~=1.20.50",
        "nltk~=3.7",
        "scikit-learn~=1.0.2",
        "Sastrawi~=1.0.1",
        "setuptools~=57.0.0",
        "networkx==2.4",
    ],
)
