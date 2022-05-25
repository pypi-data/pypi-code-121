import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "pepperize.cdk-autoscaling-gitlab-runner",
    "version": "0.2.82",
    "description": "AWS CDK GitLab Runner autoscaling on EC2 instances using docker+machine executor.",
    "license": "MIT",
    "url": "https://github.com/pepperize/cdk-autoscaling-gitlab-runner.git",
    "long_description_content_type": "text/markdown",
    "author": "Patrick Florek<patrick.florek@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pepperize/cdk-autoscaling-gitlab-runner.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "pepperize_cdk_autoscaling_gitlab_runner",
        "pepperize_cdk_autoscaling_gitlab_runner._jsii"
    ],
    "package_data": {
        "pepperize_cdk_autoscaling_gitlab_runner._jsii": [
            "cdk-autoscaling-gitlab-runner@0.2.82.jsii.tgz"
        ],
        "pepperize_cdk_autoscaling_gitlab_runner": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.8.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.59.0, <2.0.0",
        "pepperize.cdk-private-bucket>=0.0.34, <0.0.35",
        "pepperize.cdk-security-group>=0.0.26, <0.0.27",
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
