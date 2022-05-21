import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "shady-island",
    "version": "0.0.1.a26",
    "description": "Utilities and constructs for the AWS CDK",
    "license": "Apache-2.0",
    "url": "https://libreworks.github.io/shady-island/",
    "long_description_content_type": "text/markdown",
    "author": "LibreWorks Contributors",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com:libreworks/shady-island.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "shady_island",
        "shady_island._jsii"
    ],
    "package_data": {
        "shady_island._jsii": [
            "shady-island@0.0.1-alpha.26.jsii.tgz"
        ],
        "shady_island": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.12.0, <3.0.0",
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
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
