import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-eks-cluster-module",
    "version": "0.0.11",
    "description": "@smallcase/cdk-eks-cluster-module",
    "license": "Apache-2.0",
    "url": "https://github.com/smallcase/cdk-eks-cluster-module.git",
    "long_description_content_type": "text/markdown",
    "author": "@InfraTeam<bharat.parmar@smallcase.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/smallcase/cdk-eks-cluster-module.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_eks_cluster_module",
        "cdk_eks_cluster_module._jsii"
    ],
    "package_data": {
        "cdk_eks_cluster_module._jsii": [
            "cdk-eks-cluster-module@0.0.11.jsii.tgz"
        ],
        "cdk_eks_cluster_module": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib==2.22.0",
        "cdk8s==2.2.74",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.57.0, <2.0.0",
        "publication>=0.0.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
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
