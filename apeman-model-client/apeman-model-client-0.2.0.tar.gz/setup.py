import setuptools
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="apeman-model-client",  # This is the name of the package
    version="0.2.0",  # The initial release version
    author="Apeman",  # Full name of the author
    author_email='admin@apeman.com',
    description="Apeman model service client SDK",
    long_description=long_description,  # Long description read from the the readme file
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],  # Information to filter the project on PyPi website
    python_requires='>=3.7',  # Minimum version requirement of the package
    install_requires=[
        'grpcio==1.44.0',
        'protobuf==3.20.0'
    ],
    include_package_data=True,
    packages=find_packages(where="src"),
    package_dir={'': 'src'}
)
