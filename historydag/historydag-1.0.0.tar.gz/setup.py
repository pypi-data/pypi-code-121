import setuptools
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="historydag",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Will Dumm",
    author_email="wdumm88@gmail.com",
    description="Basic history DAG implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://matsengrp.github.io/historydag",
    packages=["historydag"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=["six", "PyQt5", "ete3", "biopython", "graphviz"],
)
