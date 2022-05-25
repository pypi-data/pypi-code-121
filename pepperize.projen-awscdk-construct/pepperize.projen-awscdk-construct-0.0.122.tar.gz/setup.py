import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "pepperize.projen-awscdk-construct",
    "version": "0.0.122",
    "description": "This project provides a projen project type providing presets for an AWS CDK construct library project",
    "license": "MIT",
    "url": "https://github.com/pepperize/projen-awscdk-construct.git",
    "long_description_content_type": "text/markdown",
    "author": "Patrick Florek<patrick.florek@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pepperize/projen-awscdk-construct.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "pepperize_projen_awscdk_construct",
        "pepperize_projen_awscdk_construct._jsii"
    ],
    "package_data": {
        "pepperize_projen_awscdk_construct._jsii": [
            "projen-awscdk-construct@0.0.122.jsii.tgz"
        ],
        "pepperize_projen_awscdk_construct": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "jsii>=1.58.0, <2.0.0",
        "projen>=0.50.33, <0.51.0",
        "publication>=0.0.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
