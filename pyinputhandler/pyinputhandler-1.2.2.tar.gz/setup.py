from os import name
from setuptools import setup, find_packages


with open("README.md", "r") as readme:
    description = readme.read()

setup(
    name="pyinputhandler",
    version="1.2.2",
    author="DaHunterTime",
    description="A (basic) cross-platform python input handler",
    long_description=description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/DaHunterTime/InputHandler",
    project_urls={
        "Bug Tracker": "https://github.com/DaHunterTime/InputHandler/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
)
