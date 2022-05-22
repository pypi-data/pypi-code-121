import pathlib
from setuptools import setup, find_packages


VERSION = "0.1.4"

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="pylypenko_first_package",
    version=VERSION,
    description="My(Volodymyr Pylypenko) first package",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/VovaPylypenko",
    author="Volodymyr Pylypenko",
    author_email="pylypenko@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    # packages=[""],
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,
    install_requires=[],
    # entry_points={
    #     "console_scripts": [
    #         "pylypenko_first_package=*:main",
    #     ]
    # },
)
