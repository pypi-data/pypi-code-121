import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-amazon-chime-resources",
    "version": "0.1.5",
    "description": "cdk-amazon-chime-resources",
    "license": "Apache-2.0",
    "url": "https://github.com/cdklabs/cdk-amazon-chime-resources.git",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdklabs/cdk-amazon-chime-resources.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_amazon_chime_resources",
        "cdk_amazon_chime_resources._jsii"
    ],
    "package_data": {
        "cdk_amazon_chime_resources._jsii": [
            "cdk-amazon-chime-resources@0.1.5.jsii.tgz"
        ],
        "cdk_amazon_chime_resources": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.24.0, <3.0.0",
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
