import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="django-omise",
    version="0.2.1",
    description="Django models for Omise",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/jamesx00/django-omise",
    author="James Tansiri",
    author_email="tansirijames@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "omise",
    ],
)
