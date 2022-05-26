#!/usr/bin/env python

from setuptools import setup, find_packages  # type: ignore

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    author="Yury",
    author_email="yury-m@hotmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
    ],
    description="Calculates cenROC ",
    install_requires=[],
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    package_data={"cenroctest": ["py.typed"]},
    include_package_data=True,
    keywords="cenroctest",
    name="cenroctest",
    package_dir={"": "src"},
    packages=find_packages(include=["src/cenroctest", "src/cenroctest.*"]),
    setup_requires=[],
    url="https://github.com/YuryMoskaltsov/cenroctest",
    version="0.0.8",
    zip_safe=False,
)
