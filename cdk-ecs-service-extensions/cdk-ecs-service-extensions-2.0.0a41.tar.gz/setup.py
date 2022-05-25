import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-ecs-service-extensions",
    "version": "2.0.0.a41",
    "description": "@aws-cdk-containers/ecs-service-extensions",
    "license": "Apache-2.0",
    "url": "https://github.com/cdklabs/cdk-ecs-service-extensions.git",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdklabs/cdk-ecs-service-extensions.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_ecs_service_extensions",
        "cdk_ecs_service_extensions._jsii"
    ],
    "package_data": {
        "cdk_ecs_service_extensions._jsii": [
            "ecs-service-extensions@2.0.0-alpha.41.jsii.tgz"
        ],
        "cdk_ecs_service_extensions": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.8.0, <3.0.0",
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
