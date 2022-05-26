from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.6'
DESCRIPTION = 'Survival Package creating cenROC object'
LONG_DESCRIPTION = 'A package that allows to calculate survival cutpoints based on times and events'

# Setting up
setup(
    name="cenROCTest",
    version=VERSION,
    author="Yury Moskaltsov",
    author_email="yury-m@hotmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy', 'pandas', 'matplotlib', 'scipy','statsmodels'],
    keywords=['python', 'cenROC', 'survival'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)