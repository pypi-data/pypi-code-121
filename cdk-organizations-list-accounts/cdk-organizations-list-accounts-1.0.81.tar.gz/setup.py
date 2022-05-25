import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-organizations-list-accounts",
    "version": "1.0.81",
    "description": "cdk-organizations-list-accounts is an AWS CDK building library that outputs a list of AWS organization accounts in CSV format.",
    "license": "Apache-2.0",
    "url": "https://github.com/hayao-k/cdk-organizations-list-accounts.git",
    "long_description_content_type": "text/markdown",
    "author": "hayao-k<30886141+hayao-k@users.noreply.github.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/hayao-k/cdk-organizations-list-accounts.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_organizations_list_accounts",
        "cdk_organizations_list_accounts._jsii"
    ],
    "package_data": {
        "cdk_organizations_list_accounts._jsii": [
            "cdk-organizations-list-accounts@1.0.81.jsii.tgz"
        ],
        "cdk_organizations_list_accounts": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.10.0, <3.0.0",
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
