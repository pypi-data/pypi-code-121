"""Set up the shareloc_utils package."""
import json
from pathlib import Path

from setuptools import find_packages, setup

DESCRIPTION = "Utility tools for ShareLoc.XYZ"

ROOT_DIR = Path(__file__).parent.resolve()
README_FILE = ROOT_DIR / "README.md"
LONG_DESCRIPTION = README_FILE.read_text(encoding="utf-8")
VERSION_FILE = ROOT_DIR / "shareloc_utils" / "VERSION"
VERSION = json.loads(VERSION_FILE.read_text())["version"]

REQUIRES = ["numpy", "pyyaml", "pillow", "tqdm"]

setup(
    name="shareloc-utils",
    version=VERSION,
    url="https://github.com/imodpasteur/shareloc_utils",
    author="imod-pasteur",
    author_email="shareloc@pasteur.fr",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license="MIT",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    install_requires=REQUIRES,
    extras_require={"potree": ["pypotree"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet",
    ],
)
