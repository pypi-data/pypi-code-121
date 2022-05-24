import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "renovosolutions.aws-cdk-one-time-event",
    "version": "1.0.138",
    "description": "AWS CDK Construct Library to create one time event schedules.",
    "license": "Apache-2.0",
    "url": "https://github.com/RenovoSolutions/cdk-library-one-time-event.git",
    "long_description_content_type": "text/markdown",
    "author": "Renovo Solutions<webmaster+cdk@renovo1.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/RenovoSolutions/cdk-library-one-time-event.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "one_time_event",
        "one_time_event._jsii"
    ],
    "package_data": {
        "one_time_event._jsii": [
            "cdk-library-one-time-event@1.0.138.jsii.tgz"
        ],
        "one_time_event": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk.aws-events>=1.157.0, <2.0.0",
        "aws-cdk.core>=1.157.0, <2.0.0",
        "constructs>=3.2.27, <4.0.0",
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
