import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "aws-cdk.aws-servicediscovery",
    "version": "1.157.0",
    "description": "The CDK Construct Library for AWS::ServiceDiscovery",
    "license": "Apache-2.0",
    "url": "https://github.com/aws/aws-cdk",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/aws/aws-cdk.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "aws_cdk.aws_servicediscovery",
        "aws_cdk.aws_servicediscovery._jsii"
    ],
    "package_data": {
        "aws_cdk.aws_servicediscovery._jsii": [
            "aws-servicediscovery@1.157.0.jsii.tgz"
        ],
        "aws_cdk.aws_servicediscovery": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk.aws-ec2==1.157.0",
        "aws-cdk.aws-elasticloadbalancingv2==1.157.0",
        "aws-cdk.aws-route53==1.157.0",
        "aws-cdk.core==1.157.0",
        "constructs>=3.3.69, <4.0.0",
        "jsii>=1.58.0, <2.0.0",
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
        "License :: OSI Approved",
        "Framework :: AWS CDK",
        "Framework :: AWS CDK :: 1"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
