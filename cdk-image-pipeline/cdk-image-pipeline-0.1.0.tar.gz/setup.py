import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-image-pipeline",
    "version": "0.1.0",
    "description": "Quickly deploy a complete EC2 Image Builder Image Pipeline using CDK",
    "license": "MIT-0",
    "url": "https://github.com/aws-samples/cdk-image-pipeline.git",
    "long_description_content_type": "text/markdown",
    "author": "Cameron Magee<magcamer@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/aws-samples/cdk-image-pipeline.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_image_pipeline",
        "cdk_image_pipeline._jsii"
    ],
    "package_data": {
        "cdk_image_pipeline._jsii": [
            "cdk-image-pipeline@0.1.0.jsii.tgz"
        ],
        "cdk_image_pipeline": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.23.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
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
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
