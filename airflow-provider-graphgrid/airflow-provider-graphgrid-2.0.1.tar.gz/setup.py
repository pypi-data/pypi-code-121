import os
from pathlib import Path
from setuptools import setup, find_packages

PACKAGE_NAME = "airflow-provider-graphgrid"

top_level_path = Path(__file__).parent.absolute()
with open(os.path.join(top_level_path, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name=PACKAGE_NAME,
    version="2.0.1",
    packages=find_packages(),
    url="https://docs.graphgrid.com/2.0/#/",
    entry_points={
        "apache_airflow_provider": [
            "provider_info=graphgrid_provider.__init__:get_provider_info"
        ]
    },
    license="Apache License 2.0",
    author="graphgrid",
    author_email="",
    description="GraphGrid Provider Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=[
        "apache-airflow>=2.2.2",
        "apache-airflow-providers-docker>=2.3.0"
    ],
    python_requires="!=3.9.*, >=3.6",
)
