from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="sqlserver",
    long_description=long_description,
    long_description_content_type='text/markdown',
    version="0.0.13",
    author="Ashlin Darius Govindasamy",
    author_email="adg@adgstudios.co.za",
    url="https://www.adgstudios.co.za",
    description="a module that makes queries easier to SQL Server than PYODBC",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT', 
    install_requires=["pyodbc","pandas"]
)