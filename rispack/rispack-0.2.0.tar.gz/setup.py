import setuptools

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
    author="Rispar Tecnologia",
    author_email="tecnologia@rispar.com.br",
    url="https://github.com/risparfinance/rispack",
    name="rispack",
    version="0.2.0",
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    package_data={"rispack": ["LICENSE"]},
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="Rispack - Pack of shared libraries from Rispar",
    license="Apache License 2.0",
    install_requires=["boto3", "aws-lambda-powertools", "SQLAlchemy", "marshmallow", "marshmallow_dataclass", "requests-aws-sign"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
)
