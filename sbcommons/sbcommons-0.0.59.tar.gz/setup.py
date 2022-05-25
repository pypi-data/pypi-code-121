import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="sbcommons",
    version="0.0.59",
    author="Haypp Group",
    author_email="data@hayppgroup.com",
    description="Packages shared between lambda functions and other systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Snusbolaget/lambdas",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "boto3>=1.9.75",
        "botocore>=1.12.253",
        "urllib3>=1.24.1",
        "requests>=2.22.0",
    ]
)
