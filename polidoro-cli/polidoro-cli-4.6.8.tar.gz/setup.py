"""
Setup to create the package
"""
import re
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


def get_version():
    with open('polidoro_cli/__init__.py', 'r') as init_file:
        for line in init_file.readlines():
            if 'VERSION' in line:
                return re.search(r'[\d.]+', line).group()


setup(
    name='polidoro-cli',
    version=get_version(),
    description='Polidoro CLI.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/heitorpolidoro/polidoro-cli',
    author='Heitor Polidoro',
    scripts=['bin/cli'],
    license='MIT',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
    install_requires=['polidoro-argument >= 4.0', 'pyyaml'],
    include_package_data=True
)
