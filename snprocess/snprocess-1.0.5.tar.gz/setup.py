"""
Python package configuration for scripts.

Thomas Dokas <dokastho@umich.edu>
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='snprocess',
    version='1.0.5',
    author="Thomas Dokas",
    author_email="dokastho@umich.edu",
    description="A SNP processing package",
    url="https://github.com/dokastho/snprocess",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=['snprocess', 'qc', 'templates'], exclude=['testout']),
    include_package_data=True,
    install_requires=[
        'pycodestyle',
        'pydocstyle',
        'pylint',
        'pytest',
        'pytest-mock',
        'click',
        'matplotlib',
        'pandas',
        'jinja2',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'snprocess = snprocess.__main__:main'
        ]
    },
)
