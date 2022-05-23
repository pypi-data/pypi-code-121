from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="lf",
    version="0.1.7",
    description="Tools for interacting with GT's LF AWESOME Receiver data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="David Richardson",
    author_email="drichardson42@gatech.edu",
    url="https://github.gatech.edu/LF-Group/lfdata",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 or later "
        "(GPLv3+)",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
    ],
    install_requires=[
        "scipy",
        "numpy",
        "sklearn",
        "geographiclib",
        "pandas",
        "pysolar>=0.8",
        "matplotlib",
        "datetime",
    ],
    extras_require={
        "dev": ["twine", "sphinx==3.2.1"],
        "docs": ["sphinx==3.2.1"],
    },
)
