from setuptools import setup, find_packages
from setuptools.command.install import install
from subprocess import getoutput

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

def setup_package():
    setup(name="formal_writing_checker",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    )

if __name__ == "__main__":
    setup_package()