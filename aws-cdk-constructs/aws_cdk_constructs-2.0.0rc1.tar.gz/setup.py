import setuptools
import os
import re

with open("README.md") as fp:
    long_description = fp.read()

# reading pymlconf version (same way sqlalchemy does)
with open(os.path.join(os.path.dirname(__file__), "aws_cdk_constructs", "__init__.py")) as v_file:
    package_version = (
        re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)
    )

setuptools.setup(
    name="aws_cdk_constructs",
    version=package_version,
    description="AWS CDK constructs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="author",
    author_email="author@foa.org",
    packages=setuptools.find_packages(include=["aws_cdk_constructs", "aws_cdk_constructs.*"]),
    include_package_data=True,
    url="https://bitbucket.org/cioapps/aws-cdk-constructs",
    install_requires=[
        "aws-cdk-lib==2.25.0",
        "constructs>=10.0.0,<11.0.0",
        "boto3==1.23.6",
        "cloudcomponents.cdk-cloudfront-authorization==2.1.0",
        "cloudcomponents.cdk-lambda-at-edge-pattern==2.1.0"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
