from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.7'
DESCRIPTION = 'Number patterns in a sequence'
LONG_DESCRIPTION = 'This project is created to identify the number patterns on a given number sequence which will get the difference in sequence and general term or general ratio.'

# Setting up
setup(
    name="numpatt-sequence",
    version=VERSION,
    author="Dilith Achlan",
    author_email="<dilith.achalan@outlook.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'number', 'patterns',
              'number patterns', 'sequence', 'general term'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
