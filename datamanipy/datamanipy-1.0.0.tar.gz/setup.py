from setuptools import setup, find_packages

setup(
    name="datamanipy",
    version="1.0.0",
    author="Alexandre Le Potier",
    description="A Python package that provides tools to help you manipulating data.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(include="datamanipy.*"),
    python_requires=">=3.9",
    install_requires=[
        'sqlalchemy',
        'pandas',
        'datetime',
        'getpass',
        'keyring',
        'json',
        'pathlib',
        'os']
)