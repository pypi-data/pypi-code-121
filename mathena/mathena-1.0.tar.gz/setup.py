from distutils.core import setup

import setuptools


def readme() -> str:
    with open(r"README.md") as f:
        README = f.read()
    return README


setup(
    name="mathena",
    packages=setuptools.find_packages(),
    version="1.0",
    license="MIT",
    description="it eases maths",
    author="Naman Sharma",
    author_email="namansharma232009@gmail.com",
    url="https://github.com/Naman23-coder/mathena",
    include_package_data=True,
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
