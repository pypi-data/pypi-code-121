from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="TopgreenerApi",                     # This is the name of the package
    version="0.8.4",                        # The initial release version
    author="Raphael Budd",                     # Full name of the author
    description="Library for using Topgreener devices from Python",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['test']),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    #package_dir={"": "topgreenerapi"},
    install_requires=["aiohttp", "StrEnum"]                     # Install other dependencies if any
)
