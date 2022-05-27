from os import path
from setuptools import setup
import sys
sys.path.append("src/lhcb_ftcalib")
from _version import __version__

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name         = "lhcb_ftcalib",
    version      = __version__,
    description  = "Library for calibrating flavour tagging algorithms at LHCb",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    py_modules   = [ "lhcb_ftcalib" ],
    packages     = [ "lhcb_ftcalib" ],
    license      = "GPLv3",
    package_dir  = {'': 'src'},
    url          = "https://gitlab.cern.ch/lhcb-ft/lhcb_ftcalib",
    author       = "Vukan Jevtic, Quentin Führing",
    author_email = "vukan.jevtic@cern.ch",
    classifiers  = [
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
    ],
    install_requires = [
        "numpy<=1.21",
        "pandas",
        "scipy",
        "iminuit>2.3.0",
        "matplotlib",
        "numba",
        "argparse",
        "uproot>=4"
    ],
    extras_require = {
        "dev" : [
            "pytest>4"
        ]
    },
    entry_points={
        "console_scripts": [
            "ftcalib=lhcb_ftcalib.__main__:main"
        ]
    }
)
