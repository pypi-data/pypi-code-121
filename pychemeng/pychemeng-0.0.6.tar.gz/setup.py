from setuptools import setup, find_packages

with open("README.md","r") as fh:
    long_description = fh.read()

classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Opreating system :: OS Independent"
    ]


setup(
    name='pychemeng',
    version='0.0.6',
    description='package for understanding adsorption isotherms and kinetics',
    author='Ashane Fernando',
    author_email='ashfern@yahoo.com',
    py_modules=["adsorption","kinetics"],
    package_dir={'':'src'},
    long_description=long_description,
    long_description_content_type='text/markdown',
)