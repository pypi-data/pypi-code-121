import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "pepperize.cdk-vpc",
    "version": "0.0.150",
    "description": "Utility constructs for tagging subnets or creating a cheaper vpc.",
    "license": "MIT",
    "url": "https://github.com/pepperize/cdk-vpc.git",
    "long_description_content_type": "text/markdown",
    "author": "Patrick Florek<patrick.florek@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pepperize/cdk-vpc.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "pepperize_cdk_vpc",
        "pepperize_cdk_vpc._jsii"
    ],
    "package_data": {
        "pepperize_cdk_vpc._jsii": [
            "cdk-vpc@0.0.150.jsii.tgz"
        ],
        "pepperize_cdk_vpc": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.1.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.59.0, <2.0.0",
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
