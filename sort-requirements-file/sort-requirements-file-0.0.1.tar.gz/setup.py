from setuptools import setup
import re

requirements = []

version = ""
with open("sort_requirements_file/__init__.py") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

readme = ""
with open("README.md") as f:
    readme = f.read()

extras_require = {"dev": ["black"], "docs": ["sphinx", "furo", "myst-parser"]}

packages = ["sort_requirements_file"]

setup(
    name="sort-requirements-file",
    author="HigherOrderLogic",
    url="https://github.com/HigherOrderLogic/sort-requirements-file",
    version=version,
    packages=packages,
    license="MIT",
    description="A package used to sort you requirements file.",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
    python_requires=">=3.8.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
