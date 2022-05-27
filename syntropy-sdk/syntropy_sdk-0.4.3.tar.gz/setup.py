# coding: utf-8
import os
import time

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(os.path.join(this_directory, "requirements.in"), encoding="utf-8") as f:
    requirements = f.read()
    requirements = [
        requirement
        for requirement in requirements.splitlines()
        if requirement and not requirement.startswith("#")
    ]

try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import find_packages, setup

if os.environ.get("CI_SYNTROPY_VERSION"):
    version = os.environ["CI_SYNTROPY_VERSION"]
else:
    # Development version of the package
    version = "devel"

setup(
    name="syntropy_sdk",
    py_modules=["syntropy_sdk"],
    version=version,
    url="https://github.com/syntropynet/syntropy-python-sdk/",
    author="Andrius Mikonis",
    author_email="andrius@syntropynet.com",
    description="Syntropy SDK for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.6",
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
