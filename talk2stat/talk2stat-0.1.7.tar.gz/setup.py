import os
import setuptools

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.txt')) as f:
    long_description = f.read()

setuptools.setup(
    name="talk2stat",
    version="0.1.7",
    author="Haim Bar",
    author_email="haim.bar@uconn.edu",
    description="Open a bidirectional pipe to R, julia, matlab, or python (etc.) and communicate with it via a socket.",
    url = "https://pypi.org/project/talk2stat/",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['talk2stat'],
    install_requires=["pexpect"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
