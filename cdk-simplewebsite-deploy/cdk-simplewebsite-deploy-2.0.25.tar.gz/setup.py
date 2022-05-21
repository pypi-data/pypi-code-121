import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-simplewebsite-deploy",
    "version": "2.0.25",
    "description": "This is an AWS CDK v2 Construct to simplify deploying a single-page website use CloudFront distributions.",
    "license": "Apache-2.0",
    "url": "https://github.com/SnapPetal/cdk-simplewebsite-deploy",
    "long_description_content_type": "text/markdown",
    "author": "Thon Becker<thon.becker@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/SnapPetal/cdk-simplewebsite-deploy"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_simplewebsite_deploy",
        "cdk_simplewebsite_deploy._jsii"
    ],
    "package_data": {
        "cdk_simplewebsite_deploy._jsii": [
            "cdk-simplewebsite-deploy@2.0.25.jsii.tgz"
        ],
        "cdk_simplewebsite_deploy": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.25.0, <3.0.0",
        "constructs>=10.1.13, <11.0.0",
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
