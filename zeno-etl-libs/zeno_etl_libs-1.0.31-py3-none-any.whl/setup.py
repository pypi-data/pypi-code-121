from setuptools import setup, find_packages

# for glue jobs, we need constant version, so separate setup file
setup(
    name="zeno_etl_pkg",
    version="0.0.6",
    packages=find_packages()
)
