import sys
from setuptools import setup, find_packages
from distutils.util import convert_path


if sys.version_info < (3, 7):
    raise RuntimeError("biblebot requires Python 3.7+")

with open("README.md", "r", encoding="UTF-8") as f:
    long_description = f.read()

about = {}
with open(convert_path("biblebot/__version__.py")) as f:
    exec(f.read(), about)


setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    maintainer=", ".join((f'{about["__author__"]} <{about["__author_email__"]}>', *about["__contributors__"])),
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=about["__url__"],
    packages=find_packages(),
    install_requires=["beautifulsoup4 >= 4.8.0"],
    extras_require={"http": ["aiohttp[speedups]>=3.6.2"]},
    python_requires=">=3.7",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)
