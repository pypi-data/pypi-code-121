from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'


DESCRIPTION = 'Cleaning and standardizing feature values of the products'

# Setting up
setup(
    name="DataQualityTransformation",
    version=VERSION,
    author="GHonem",
    author_email="<mahmoud.gh2016@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    package_data={'': ['*.yml']},
    install_requires=['colour', 'word2number'],
    keywords=['python', 'dataquality'],
    include_package_data=True,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
