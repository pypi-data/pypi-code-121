from setuptools import setup, find_packages

setup(
    name="perun.connector",
    python_requires=">=3.9",
    url="https://github.com/CESNET/perun.connector.git",
    description="Module for communication with Perun IAM system",
    packages=find_packages(),
    install_requires=[
        "setuptools",
        "urllib3>=1.26.9,<2",
        "python-dateutil>=2.8.2,<3",
        "PyYAML>=6.0,<7",
        "ldap3>=2.9.1,<3",
        "pycurl>=7.45.1,<8",
        "jsonpatch>=1.22,<2",
    ],
)
