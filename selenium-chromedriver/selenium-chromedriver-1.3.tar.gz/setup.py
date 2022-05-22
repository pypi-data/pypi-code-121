from sys import modules
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='selenium-chromedriver',  
    version='1.3',
    author="Tejas M R",
    author_email="totejasmr@gmail.com",
    description="Install Stable version Chromedriver for Selenium on Windows, MacOS, M1 MacOS and Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tezz-io/selenium-chromedriver",
    packages=setuptools.find_packages(),
    project_urls={
        "Bug Tracker": "https://github.com/tezz-io/selenium-chromedriver/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)