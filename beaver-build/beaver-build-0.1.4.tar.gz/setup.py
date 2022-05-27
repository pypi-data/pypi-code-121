import re
from setuptools import find_packages, setup


# Load the README and strip out Sphinx directives that PyPI cannot handle.
with open("README.rst") as fp:
    long_description = fp.read()
replacements = [
    (".. doctest::", ".. code-block:: python"),
    (".. testcode::", ".. code-block:: python"),
    (":math:", ":code:"),
    (":func:", ":code:"),
    (":class:", ":code:"),
    (":meth:", ":code:"),
    (":mod:", ":code:"),
]
for old, new in replacements:
    long_description = long_description.replace(old, new)
long_description = re.sub(
    r"((\.\. automodule:: .*?$)|(\.\. toctree::)|(\.\. plot:: .*?$))", r".. code-block::\n\n  \1",
    long_description, flags=re.MULTILINE
)

# Load the version number.
try:
    with open('VERSION') as fp:
        version = fp.read().strip()
except FileNotFoundError:
    version = 'dev'

setup(
    name="beaver-build",
    packages=find_packages(),
    author="Till Hoffmann",
    author_email="niches_osmosis0a@icloud.com",
    version=version,
    install_requires=[
        "aiohttp",
    ],
    long_description=long_description,
    long_description_content_type="text/x-rst",
    extras_require={
        "tests": [
            "flake8",
            "pytest",
            "pytest-cov",
            "twine",
        ],
        "docs": [
            "sphinx",
            "sphinx_rtd_theme",
            "sphinx-argparse",
        ]
    },
    entry_points={
        "console_scripts": [
            "beaver = beaver_build.cli:__main__",
        ]
    },
)
