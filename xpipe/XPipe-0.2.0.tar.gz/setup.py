from setuptools import find_packages, setup
import os 

# Source : MLflow repository https://github.com/mlflow/mlflow/blob/master/setup.py
# Get a list of all files in the JS directory to include in our module

with open("README.rst", "r") as fh:
    long_description = fh.read()

config_extra_requirements = ["pyyaml"]
server_extra_requirements = ["numpy", "bokeh", "mongoengine", "Flask", "flask-cors", "pyyaml", "click", "gunicorn"]

setup(
    name="XPipe",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    packages=find_packages(),
    version = "0.2.0",
    description="Standardize your ML projects",
    author="Jules Tevissen",
    license="MIT",
    install_requires=[
        "pyyaml"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)