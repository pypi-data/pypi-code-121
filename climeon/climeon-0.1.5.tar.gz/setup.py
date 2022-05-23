# pylint: disable=missing-module-docstring

from setuptools import setup, find_packages

PYPI_DESCRIPTION = "Climeon API client"

setup(
    name="climeon",
    packages=find_packages(),
    version="0.1.5",
    license="MIT",
    description=PYPI_DESCRIPTION,
    long_description=PYPI_DESCRIPTION,
    author="Emil Hjelm",
    author_email="emil.hjelm@climeon.com",
    keywords=["climeon", "REST", "API"],
    python_requires=">=3.7.1",
    install_requires=[
        "matplotlib",
        "msal",
        "pandas",
        "requests"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Operating System :: OS Independent"
    ]
)
