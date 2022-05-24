import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "renovosolutions.aws-cdk-certbot",
    "version": "1.1.102",
    "description": "AWS CDK Construct Library to manage Lets Encrypt certificate renewals with Certbot",
    "license": "Apache-2.0",
    "url": "https://github.com/RenovoSolutions/cdk-library-certbot.git",
    "long_description_content_type": "text/markdown",
    "author": "Renovo Solutions<webmaster+cdk@renovo1.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/RenovoSolutions/cdk-library-certbot.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "certbot",
        "certbot._jsii"
    ],
    "package_data": {
        "certbot._jsii": [
            "cdk-library-certbot@1.1.102.jsii.tgz"
        ],
        "certbot": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk.aws-events-targets>=1.157.0, <2.0.0",
        "aws-cdk.aws-events>=1.157.0, <2.0.0",
        "aws-cdk.aws-iam>=1.157.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.157.0, <2.0.0",
        "aws-cdk.aws-route53>=1.157.0, <2.0.0",
        "aws-cdk.aws-s3>=1.157.0, <2.0.0",
        "aws-cdk.aws-sns-subscriptions>=1.157.0, <2.0.0",
        "aws-cdk.aws-sns>=1.157.0, <2.0.0",
        "aws-cdk.core>=1.157.0, <2.0.0",
        "constructs>=3.2.27, <4.0.0",
        "jsii>=1.59.0, <2.0.0",
        "publication>=0.0.3",
        "renovosolutions.aws-cdk-one-time-event>=1.0.37, <2.0.0"
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
