from setuptools import setup, find_packages
import os

with open(os.path.join("inflationpy", "version.txt")) as file_handler:
    __version__ = file_handler.read().strip()

CLASSIFIERS = """\
Intended Audience :: Science/Research
License :: OSI Approved :: BSD License
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3 :: Only
"""


if __name__ == "__main__":
    setup(
        name="inflationpy",
        version=__version__,
        author="Martin Vasar",
        author_email="vasarmartin0@gmail.com",
        keywords="cosmology scalar-tensor-theory cosmic-inflation",
        packages=[package for package in find_packages() if package.startswith("inflationpy")],
        package_data={"inflationpy": ["py.typed", "version.txt", "data/sigma1.dat", "data/sigma2.dat"]},
        install_requires=[
            "numpy",
            "scipy",
            "sympy",
            "mpmath",
            "matplotlib",
        ],
        extras_require={
            "tests": [
                # Run tests
                "pytest>=6.0",
                # Linter
                "flake8>=3.8",
                # Reformat
                "black",
            ],
            "docs": [
                "sphinx",
                "sphinx-autobuild",
                "sphinx-rtd-theme",
                # For spelling
                "sphinxcontrib.spelling",
                # Type hints support
                "sphinx-autodoc-typehints",
            ],
        },
        classifiers=[_f for _f in CLASSIFIERS.split("\n") if _f],
        python_requires=">=3.7",
    )
