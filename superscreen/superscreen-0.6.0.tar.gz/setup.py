"""
# SuperScreen

![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/loganbvh/superscreen/lint-and-test/main) [![Documentation Status](https://readthedocs.org/projects/superscreen/badge/?version=latest)](https://superscreen.readthedocs.io/en/latest/?badge=latest) [![codecov](https://codecov.io/gh/loganbvh/superscreen/branch/main/graph/badge.svg?token=XW7LSY8WVD)](https://codecov.io/gh/loganbvh/superscreen) ![GitHub](https://img.shields.io/github/license/loganbvh/superscreen) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![DOI](https://zenodo.org/badge/376110557.svg)](https://zenodo.org/badge/latestdoi/376110557)

SuperScreen is a package for simulating the magnetic response of multi-planar thin film
superconducting devices. SuperScreen solves the coupled Maxwell's and London equations
on a triangular mesh using a matrix inversion method described in the following references:

1. Phys. Rev. B 72, 024529 (2005).
2. Rev. Sci. Instrum. 87, 093702 (2016).
3. Supercond. Sci. Technol. 29 (2016) 124001.

The documentation for `SuperScreen` can be found at [superscreen.readthedocs.io](https://superscreen.readthedocs.io/en/latest/).

## Try `SuperScreen`

Click the badge below and navigate to `docs/notebooks/` to try `SuperScreen` interactively online via [Binder](https://mybinder.org/):

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/loganbvh/superscreen/HEAD)

"""

from setuptools import setup, find_packages

DESCRIPTION = "SuperScreen: simulate Meissner screening in 2D superconducting devices."
LONG_DESCRIPTION = __doc__

NAME = "superscreen"
AUTHOR = "Logan Bishop-Van Horn"
AUTHOR_EMAIL = "logan.bvh@gmail.com"
URL = "https://github.com/loganbvh/superscreen"
LICENSE = "MIT"
PYTHON_VERSION = ">=3.7, <3.10"

INSTALL_REQUIRES = [
    "dill",
    "ipython",
    "jupyter",
    "matplotlib",
    "meshpy",
    "numpy",
    "optimesh",
    "pandas",
    "pint",
    "pre-commit",
    "pytest",
    "pytest-cov",
    "ray[default]",
    "scipy",
    "shapely",
]

EXTRAS_REQUIRE = {
    "docs": [
        "sphinx",
        "sphinx_rtd_theme",
        "sphinx-autodoc-typehints",
        "nbsphinx",
        "pillow",  # required for image scaling in RTD
    ],
}

CLASSIFIERS = """\
Development Status :: 4 - Beta
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Operating System :: MacOS
Operating System :: POSIX
Operating System :: Unix
Operating System :: Microsoft :: Windows
Programming Language :: Python
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Physics
"""

CLASSIFIERS = [line for line in CLASSIFIERS.splitlines() if line]
PLATFORMS = ["Linux", "Mac OSX", "Unix", "Windows"]
KEYWORDS = "superconductor meissner screening"

exec(open("superscreen/version.py").read())

setup(
    name=NAME,
    version=__version__,  # noqa: F821
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    platforms=PLATFORMS,
    python_requires=PYTHON_VERSION,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
)
