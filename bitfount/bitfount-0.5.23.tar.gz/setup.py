"""This file enables the github repo to be packaged into a wheel using `setuptools`."""
import runpy

from setuptools import find_packages, setup

# Import version information into current namespace
file_globals = runpy.run_path("bitfount/__version__.py")

# Get security constraints
with open("requirements/constraints-security.txt") as f:
    security_constraints = f.read().splitlines()

# Get compatibility constraints
with open("requirements/constraints-compatibility.txt") as f:
    compat_constraints = f.read().splitlines()

# Get install requirements
with open("requirements/requirements.in") as f:
    install_reqs = f.read().splitlines()

# Add the security and compatibility constraints to the main requirements
# and get rid of unnecessary lines.
install_reqs.extend(security_constraints)
install_reqs.extend(compat_constraints)
install_reqs = [
    line.split("#")[0].strip()
    for line in install_reqs
    if not line.startswith(("#", "-c", "-r"))
]

# Get testing requirements
with open("requirements/requirements-tutorial.txt") as f:
    tutorial_reqs = f.read().splitlines()

# Get testing requirements
with open("requirements/requirements-test.txt") as f:
    tests_reqs = f.read().splitlines()

# Get dev requirements
with open("requirements/requirements-dev.txt") as f:
    dev_reqs = f.read().splitlines()

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    author=file_globals["__author__"],
    author_email=file_globals["__author_email__"],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Distributed Computing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    description=file_globals["__description__"],
    entry_points={
        "console_scripts": [
            "bitfount = scripts.script_runner:main",
        ]
    },
    extras_require={
        "tests": tests_reqs,
        "dev": dev_reqs,
        "tutorials": tutorial_reqs,
    },
    install_requires=install_reqs,
    keywords=["federated learning", "privacy", "AI", "machine learning"],
    license="Apache License 2.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    name=file_globals["__title__"],
    packages=find_packages(),
    package_data={"bitfount": ["py.typed"]},
    project_urls={
        "Documentation": "https://docs.bitfount.com/",
        "Homepage": "https://bitfount.com",
        "Source Code": "https://github.com/bitfount/bitfount/",
        "Hub": "https://hub.bitfount.com",
    },
    python_requires=">=3.8,<3.10",
    url=file_globals["__url__"],
    version=file_globals["__version__"],
)
