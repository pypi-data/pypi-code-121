from setuptools import setup, find_packages
import pathlib


here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="numeric-methods",
    version="1.1.0",
    description="Numeric methods is a package of tools for analyze functions via numeric methods",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Helltraitor/numeric-methods",
    author="Helltraitor",
    author_email="helltraitor@hotmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="mathematics",
    packages=find_packages(),
    python_requires=">=3.10, <4",
    license="MIT",
    project_urls={
        "Bug Reports": "https://github.com/Helltraitor/numeric-methods/issues",
        "Source": "https://github.com/Helltraitor/numeric-methods",
    },
)
