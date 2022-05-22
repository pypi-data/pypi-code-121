from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='MLNN',
    version='2.1',    
    description='Multi-layer neuron network',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='vladgap',
    author_email='gaponenko.vladimir@gmail.com',
    packages=['MLNN'],
    zip_safe=False 
)