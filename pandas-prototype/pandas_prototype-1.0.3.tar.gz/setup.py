from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.0.3'
DESCRIPTION = 'A package with implementation of famous Pandas library in my way ,  allows you to visualize data using data tables.'

# Setting up
setup(
    name="pandas_prototype",
    version=VERSION,
    license="GPL-3.0 license",
    url="https://github.com/Sanmeet007/pandas_prototype",
    author="Sanmeet Singh",
    author_email="ssanmeet123@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['json2html', 'prettytable'],
    keywords=['python', 'pandas', 'pandas prototype', 'prototyping', 'data visualizing', 'data scientist'  , 'data'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows",
    ]
)
