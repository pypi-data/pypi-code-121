import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-lex-zip-import",
    "version": "0.0.31",
    "description": "cdk construct for importing a zipped Lex bot",
    "license": "Apache-2.0",
    "url": "https://github.com/schuettc/cdk-lex-zip-import.git",
    "long_description_content_type": "text/markdown",
    "author": "Court Schuett<schuettc@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/schuettc/cdk-lex-zip-import.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_lex_zip_import",
        "cdk_lex_zip_import._jsii"
    ],
    "package_data": {
        "cdk_lex_zip_import._jsii": [
            "cdk-lex-zip-import@0.0.31.jsii.tgz"
        ],
        "cdk_lex_zip_import": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.20.0, <3.0.0",
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
