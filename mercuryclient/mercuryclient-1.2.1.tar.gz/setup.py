from os import path

from setuptools import find_packages
from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, "README.rst")) as f:
    long_description = f.read()

requirements = ["requests >=2.25.0,<3", "PyJWT >=1.7.0,<2", "pydantic >=1.7.0,<2"]
dev_requirements = ["pre-commit", "wheel", "twine"]

setup(
    name="mercuryclient",
    version="1.2.1",
    description="Python SDK for Mercury service",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://bitbucket.org/esthenos/mercury",
    author="Esthenos Technologies Private Limited",
    author_email="dinu@esthenos.com",
    license="Proprietary License",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
    python_requires=">=3.6",
    zip_safe=False,
)
