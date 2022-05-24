# PyPI upload:
#
#     $ pipenv install --dev --skip-lock
#     $ python setup.py sdist bdist_wheel --universal
#     $ twine upload dist/*
#
# Install in development:
#
#     $ python3 -m pip install -e .

from setuptools import find_packages, setup

VERSION = "0.0.4"
INSTALL_REQUIRES = ['requests >= 2.20; python_version >= "3.0"']
TESTS_REQUIRE = ["pytest"]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chaingrep",
    version=VERSION,
    author="Chaingrep",
    author_email="support@chaingrep.com",
    license="MIT",
    url="https://github.com/chaingrep/chaingrep-py",
    packages=find_packages(exclude=["tests", "tests.*"]),
    description="Python bindings for the Chaingrep API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    keywords="chaingrep api blockchain",
    project_urls={
        "Changes": "https://github.com/chaingrep/chaingrep-py/blob/main/CHANGELOG.md",
        "Source": "https://github.com/chaingrep/chaingrep-py",
        "Documentation": "https://docs.chaingrep.com",
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
