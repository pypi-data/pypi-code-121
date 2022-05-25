from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

VERSION = '1.1.2'
DESCRIPTION = 'PI Database Query Tool'
LONG_DESCRIPTION = 'A package simplifying use of PIconnect and implements robust querying functions with basic pre-processing of the queried data'

# Setting up
setup(
    name="pi_db_query",
    version=VERSION,
    author="1@0 (Anil Gurbuz)",
    author_email="<anlgrbz91@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires= ["setuptools>=58.0.4", "pandas>=1.3.4", "numpy>=1.21.2", "piconnect>=0.9.1", "tqdm>=4.62.3"],
    keywords=["OSISoft", "PI", "Query Tool"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)


