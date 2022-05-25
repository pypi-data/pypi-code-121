import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="simple_fpa",
    version="1.2",
    description="Simple nonparametric inference for sealed first-price auctions.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Pasha Andreyanov, Grigory Franguridi",
    author_email="pandreyanov@gmail.com",
    license="MIT",
    packages=["simple_fpa"],
    classifiers=[
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=['numpy','scipy','pandas'],
    include_package_data=True,
    package_data={'': ['data/*.csv']}
)