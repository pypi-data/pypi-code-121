import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "pwed-cdk",
    "version": "0.0.44",
    "description": "A library of AWS CDK constructs that I have created",
    "license": "MIT",
    "url": "https://github.com/pwed/pwed-cdk.git",
    "long_description_content_type": "text/markdown",
    "author": "Fred Stoddart<pwed@users.noreply.github.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pwed/pwed-cdk.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "pwed_cdk",
        "pwed_cdk._jsii",
        "pwed_cdk.pwed_bastion",
        "pwed_cdk.pwed_static_site"
    ],
    "package_data": {
        "pwed_cdk._jsii": [
            "pwed-cdk@0.0.44.jsii.tgz"
        ],
        "pwed_cdk": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.5.0, <3.0.0",
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
