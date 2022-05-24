# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# This call to setup() does all the work
setup(
    name="scrapper-boilerplate",
    version="0.2.1",
    description="Scrapping/Automating tools, userSwitching, anti-bot detection and more...",
    long_description_content_type="text/markdown",
    long_description=open('README.md', encoding='utf-8').read(),
    url="https://job-hunting.readthedocs.io/",
    author="Jeferson/MxJeff",
    author_email="mx.jeferson.10@hotmail.com",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "selenium", 
        "requests", 
        "pandas", 
        "beautifulsoup4", 
        "python-dotenv", 
        "python-telegram-bot",
        "lxml",
        "fake-useragent"
    ]
)