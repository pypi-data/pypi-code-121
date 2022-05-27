import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cloudstructs",
    "version": "0.5.2",
    "description": "High-level constructs for AWS CDK",
    "license": "Apache-2.0",
    "url": "https://github.com/jogold/cloudstructs.git",
    "long_description_content_type": "text/markdown",
    "author": "Jonathan Goldwasser<jonathan.goldwasser@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/jogold/cloudstructs.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cloudstructs",
        "cloudstructs._jsii"
    ],
    "package_data": {
        "cloudstructs._jsii": [
            "cloudstructs@0.5.2.jsii.tgz"
        ],
        "cloudstructs": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.1.0, <3.0.0",
        "aws-cdk.aws-apigatewayv2-alpha>=2.1.0.a0, <3.0.0",
        "aws-cdk.aws-apigatewayv2-integrations-alpha>=2.1.0.a0, <3.0.0",
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
