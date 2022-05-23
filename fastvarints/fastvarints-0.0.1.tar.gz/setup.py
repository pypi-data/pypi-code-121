import sys

try:
    from skbuild import setup
except ImportError:
    print(
        "Please update pip, you need pip 10 or greater,\n"
        " or you need to install the PEP 518 requirements in pyproject.toml yourself",
        file=sys.stderr,
    )
    raise

from setuptools import find_packages

setup(
    name="fastvarints",
    version="0.0.1",
    description="Implements the elais gamma encoding for numpy arrays",
    author="Jeffrey Wigger",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    cmake_install_dir="src/fastvarints",
    include_package_data=True,
    extras_require={"test": ["pytest", "numpy"]},
    python_requires=">=3.9",
)
