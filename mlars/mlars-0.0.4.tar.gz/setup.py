from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.4'
DESCRIPTION = 'a library for recommending ml algorithms'
LONG_DESCRIPTION = 'A package that helps you to recommend machine learning algorithms'

# Setting up
setup(
    name="mlars",
    version=VERSION,
    author="prashantm2001 , HaiderNakara",
    author_email="<prashant.om@somaiya.edu>,<haider.n@somaiya.edu>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['colorama', 'numpy', 'pandas', 'scikit-learn'],
    keywords=['python', 'video', 'machine-learning', 'recommendation'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)