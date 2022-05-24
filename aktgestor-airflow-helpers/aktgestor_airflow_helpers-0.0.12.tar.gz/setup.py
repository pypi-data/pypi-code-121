from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.12'
DESCRIPTION = 'Helper functions for ariflow.'

# Setting up
setup(
    name="aktgestor_airflow_helpers",
    version=VERSION,
    author="AktSoftware",
    author_email="<francis@aktsoftware.com.br>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['jinjasql', 'pandas'],
    keywords=[],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)