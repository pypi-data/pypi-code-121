import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sls-tools",
    version="0.0.4",
    author="Patrick Stout",
    author_email="pstout@prevagroup.com",
    license="Apache2",
    description="Utilities for developing AWS Lambda functions in Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ki-tools/sls-tools-py",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=(
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'boto3',
    ]
)
