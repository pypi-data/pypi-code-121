from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.rst").read_text(encoding="utf-8")

with open("cyclehunter/__init__.py") as file:
    for line in file:
        if line.startswith("__version__"):
            version = line.strip().split()[-1][1:-1]
            break


def parse_requirements_file(filename):
    with open(filename) as file:
        requires = [l.strip() for l in file.readlines() if not l.startswith("#")]
    return requires


install_requires = parse_requirements_file("requirements.txt")
setup(
    # There are some restrictions on what makes a valid project name
    # specification here:
    # https://packaging.python.org/specifications/core-metadata/#name
    name="cyclehunter",  # Required
    # For a discussion on single-sourcing the version across setup.py and the
    # project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,  # Required
    description="Framework for Discrete Nonlinear Dynamics and Chaos",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # url="https://cyclehunter.readthedocs.io/en/latest/index.html",  # Optional
    author="Matthew Gudorf and Ibrahim Abu-Hijleh",
    author_email="matthew.gudorf@gmail.com",  # Optional
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Microsoft :: Windows :: Windows 10",
    ],
    keywords=[
        "pde",
        "partial differential equation",
        "numeric",
        "numerical simulation",
        "solver",
        "framework",
        "periodic cycle",
    ],
    py_modules=[
        "cyclehunter.phik",
    ],
    packages=find_packages(include=["cyclehunter", "cyclehunter.*"]),
    python_requires=">=3.8",
    install_requires=['numpy', 'scipy'],
    package_data={"cyclehunter": ["requirements.txt"]},
)
