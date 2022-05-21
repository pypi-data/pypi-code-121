import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-hugo-deploy",
    "version": "0.0.7",
    "description": "Deploy Hugo static websites to AWS",
    "license": "Apache-2.0",
    "url": "https://github.com/maafk/cdk-hugo-deploy.git",
    "long_description_content_type": "text/markdown",
    "author": "Taylor Ondrey<taylor@taylorondrey.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/maafk/cdk-hugo-deploy.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_hugo_deploy",
        "cdk_hugo_deploy._jsii"
    ],
    "package_data": {
        "cdk_hugo_deploy._jsii": [
            "cdk-hugo-deploy@0.0.7.jsii.tgz"
        ],
        "cdk_hugo_deploy": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.24.1, <3.0.0",
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
