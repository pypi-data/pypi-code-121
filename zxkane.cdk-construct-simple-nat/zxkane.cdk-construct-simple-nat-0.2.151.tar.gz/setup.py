import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "zxkane.cdk-construct-simple-nat",
    "version": "0.2.151",
    "description": "A CDK construct to build Simple NAT instance on AWS.",
    "license": "Apache-2.0",
    "url": "https://github.com/zxkane/snat",
    "long_description_content_type": "text/markdown",
    "author": "Kane Zhu<me@kane.mx>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/zxkane/snat"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "zxkane.cdk_construct_simple_nat",
        "zxkane.cdk_construct_simple_nat._jsii"
    ],
    "package_data": {
        "zxkane.cdk_construct_simple_nat._jsii": [
            "cdk-construct-simple-nat@0.2.151.jsii.tgz"
        ],
        "zxkane.cdk_construct_simple_nat": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.0.0, <3.0.0",
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
