import io
import os

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    """Read a file."""
    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content

PACKAGE = "ifrn_estatistica"
NAME = "ifrn_estatistica"
DESCRIPTION = "Tabela descritiva"
AUTHOR = "Ivo Trindade"
AUTHOR_EMAIL = "haddleytrindade@gmail.com"
URL = "https://github.com/hadtrindade/ifrn-estatistica"
VERSION = "0.0.9"

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    keywords="tabela descritiva",
    url=URL,
    description=DESCRIPTION,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=read("requirements.txt"),
    platforms="linux",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Framework :: Pytest",
        "Topic :: Software Development :: Testing :: Unit",
    ],
    zip_safe=False,
)
