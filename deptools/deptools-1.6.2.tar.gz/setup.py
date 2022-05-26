import os

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("version.txt", "r") as fh:
    version_string = fh.read()

setuptools.setup(
    name="deptools",
    version=version_string,
    author="Alazar Technologies",
    author_email="support@alazartech.com",
    description="Application Deployment Tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://alazartech.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	install_requires=[
        'docopt>=0.6.2',
        "parsimonious>=0.8.1",
        "pyminizip>=0.2.4",
        "PyYAML>=5.1",
        "azure-storage-blob>=12.5.0",
        "node-semver>=0.6.1",
    ],
    entry_points={
        'console_scripts': [
            'deploy=deptools.deploy:main',
            'changelogparser=deptools.changelogparser:main',
            'runclangformat=deptools.runclangformat:main',
            'createversionfile=deptools.createversionfile:main',
            'versiontype=deptools.versiontype:main',
            'register=deptools.register:main',
        ],
    },
    package_data={'': ['CHANGELOG.md']},
    include_package_data=True,
)
