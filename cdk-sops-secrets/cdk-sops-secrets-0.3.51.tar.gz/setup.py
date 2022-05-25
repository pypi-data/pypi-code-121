import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-sops-secrets",
    "version": "0.3.51",
    "description": "CDK Constructs that syncs your sops secrets into AWS SecretsManager secrets.",
    "license": "Apache-2.0",
    "url": "https://github.com/markussiebert/cdk-sops-secrets.git",
    "long_description_content_type": "text/markdown",
    "author": "Markus Siebert<dev@markussiebert.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/markussiebert/cdk-sops-secrets.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_sops_secrets",
        "cdk_sops_secrets._jsii"
    ],
    "package_data": {
        "cdk_sops_secrets._jsii": [
            "cdk-sops-secrets@0.3.51.jsii.tgz"
        ],
        "cdk_sops_secrets": [
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
