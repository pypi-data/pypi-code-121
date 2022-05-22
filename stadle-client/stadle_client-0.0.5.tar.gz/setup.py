from setuptools import setup
from setuptools import find_packages

from tools.helpers.setup_tools import InstallationTools

"""
Setup.py Format was adopted from

References:

1. MLFLOW: https://github.com/mlflow/mlflow
2. PyTorch: https://github.com/pytorch/pytorch

When Upgrading the pip package installation make sure to test it out with the test.pypi rather than directly
testing on the pypi. Make sure to include the extra-index-url pointing to test.pypi.org/simple since we install from
the test.pypi.

>>> python3 -m pip install stadle==<version> --extra-index-url https://test.pypi.org/simple --no-cache-dir

"""

# helper utils to read files and requirements
install_tools = InstallationTools()

SETUP_REQUIRES = ['wheel', 'pytest']
long_description = install_tools.read_file_as_text("README.md")
packages = find_packages(include=["stadle", "stadle.*", "setups", "tools", "tools.*"], exclude=["prototypes"])

if __name__ == '__main__':
    setup(
        name="stadle_client",
        version="0.0.5",
        description="Stadle, A platform for federated learning.",
        package_data={'': ['setups',]},
        include_package_data=True,
        packages=packages,
        long_description=long_description,
        long_description_content_type="text/markdown",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
        ],
        url="https://github.com/tie-set/stadle_dev",
        author="Tie-Set Inc",
        author_email="package@tie-set.com",
        setup_requires=SETUP_REQUIRES,
        install_requires=install_tools.get_install_requires(),
        extras_require={
            "dev": install_tools.get_dev_requires(),
        },
    )
