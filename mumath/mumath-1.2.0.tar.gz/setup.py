from setuptools import setup, find_packages
from pathlib import Path
from distutils.util import convert_path


# Import __version__ (ugly, but works)
version = Path(__file__).parent / "mumath" / "config.py"
exec(version.read_text(encoding="utf-8"))


long_description = """
# Mumath
Mumath is a LATEX-like to MathML conversion tool written in Python.

It also includes Markdown extensions for inline `$...$` and blocks `$$...$$`
and a simple server for quick testing.

Install and open in browser:
```sh
$ pip install mumath
$ py -m mumath.server --open
```
"""

packages = find_packages()

options = {
    "name": "mumath",
    "version": __version__,
    "author": "::fourpoints",
    "description": "LATEX to MathML conversion tool",
    "long_description": long_description,
    "long_description_content_type": "text/markdown",
    "url": "https://github.com/fourpoints/mumath",
    "packages": packages,
    # "package_dir": {"": "."},
    "classifiers": [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    "package_data": {
        "mumath": ["data/index.html"],
    },
    "install_requires": [],
    "extras_require": {
        "markdown": ["markdown"],
    },
    "entry_points": {
        "markdown.extensions": [
            "mumath = mumath.markdown:MuMark",
            "mumath-inline = mumath.markdown:InlineMuMark",
        ]
    }
}

setup(**options)
