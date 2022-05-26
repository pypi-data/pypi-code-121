import setuptools
from setuptools import setup, find_packages


with open("README.md") as f:
    files = f.read()


setup(
    name='humingbird',
    version='0.5.1',
    description="Python SDK for Humingbird!",
    long_description=files,
    long_description_content_type='text/markdown',
    install_requires=[
             'Pillow>=7.1',
             'transformers>=4.19.2',
             'torch>=1.11.0'       
    ],
    license='MIT',
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"}
)


