import pathlib

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# read requirements from text
with open("requirements.txt") as f:
    required = f.read().splitlines()

# This call to setup() does all the work
setup(
    name="offline-model-builder",
    version="0.1.0",
    description="Wrapper for offline model builder module",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://mnc-repo.mncdigital.com/ai-team/vision_plus/rce_ingestor_module",
    author="AI Teams",
    author_email="ferdina.kusumah@mncgroup.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[o for o in required if "#" not in o],
)
