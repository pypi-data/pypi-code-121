from pathlib import Path
from setuptools import setup
import os


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    author="jin0g",
    author_email="akira@jinguji.me",
    description="Specify python version must in your requirements.txt",
    long_description=long_description,
    long_description_content_type='text/markdown',
    name="python-must",
    python_requires="=="+os.environ['TARGET'],
    url="https://github.com/jin0g/python-must",
    version=os.environ['TARGET'],
)
