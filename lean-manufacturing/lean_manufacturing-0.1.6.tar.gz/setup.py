from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='lean_manufacturing',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.1.6',
    packages=find_packages(include=['lean_manufacturing'])
)