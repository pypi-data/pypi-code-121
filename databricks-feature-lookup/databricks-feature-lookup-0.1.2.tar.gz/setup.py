from importlib.machinery import SourceFileLoader
import os
from setuptools import setup, find_namespace_packages
from databricks.feature_store import mlflow_model_constants

version = (
    SourceFileLoader(
        "databricks.feature_store.feature_lookup_version",
        os.path.join("databricks", "feature_store", "feature_lookup_version.py"),
    )
    .load_module()
    .VERSION
)

with open("README.md") as f:
    readme_contents = f.read()

with open("LICENSE.md") as f:
    license_contents = f.read()

# Append the text from LICENSE.md to the end of the README.md content
readme_contents_with_license = (
    readme_contents + "\n\n" + "# License" + "\n\n" + license_contents
)

# Overwrite the existing README.md file with the readme + license content for the setup() step.
# The original version will be restored to it's original state after setup() finishes.
with open("README.md", "w") as f:
    f.write(readme_contents_with_license)

setup(
    name=mlflow_model_constants.FEATURE_LOOKUP_CLIENT_PIP_PACKAGE,
    version=version,
    author_email="feedback@databricks.com",
    license="Databricks Proprietary License",
    license_files=("LICENSE.md", "NOTICE.md"),
    long_description=readme_contents_with_license,
    long_description_content_type="text/markdown",
    # The minimum required python version should align with the conda env specified by feature store client log_model()
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    packages=find_namespace_packages(include=["databricks.*"], exclude=["tests"]),
    include_package_data=True,
    package_data={
        "databricks.feature_store.utils": ["headers.yaml"],
    },
    install_requires=[
        "mlflow>=1.23.0",
        "pyyaml>=5.1",
        "sqlalchemy>=1.4.8",
        "pymysql>=1.0.2",
        "boto3>=1.19.9",
    ],
    author="Databricks",
    description="Databricks Feature Store Feature Lookup Client",
)

# Restore the README.md file to it's original state
with open("README.md", "w") as f:
    f.write(readme_contents)
