import setuptools
import shutil
import os

from setuptools.command.sdist import sdist
from wheel.bdist_wheel import bdist_wheel

with open("README.md", "r") as fh:
    long_description = fh.read()

def clean_folders():
    print("Removing temporary folders.")

    TMP_FOLDERS = ["rename_tools.egg-info", "build"]
    for folder in TMP_FOLDERS:
        if os.path.exists(folder):
            shutil.rmtree(folder)


class SdistCommand(sdist):
    """Custom build command."""

    def run(self):
        sdist.run(self)
        clean_folders()


class BdistWheelCommand(bdist_wheel):
    """Custom build command."""

    def run(self):
        bdist_wheel.run(self)
        clean_folders()


setuptools.setup(
    name="rename_tools",
    version="0.0.1",
    author="Thiago Nepomuceno",
    author_email="thiago@neps.academy",
    description="This project provide tools to rename folders and files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # include_package_data=True,
    # url="https://github.com/username/rename_tools",
    packages=setuptools.find_packages(),   
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["click", "rich"],
    cmdclass={"sdist": SdistCommand, "bdist_wheel": BdistWheelCommand},
)