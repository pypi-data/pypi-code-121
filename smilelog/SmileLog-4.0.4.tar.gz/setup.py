#import setuptools
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(
    name="SmileLog",
    version="4.0.4",
    author="Sitthykun LY",
    author_email="ly.sitthykun@gmail.com",
    description="Log library",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/sitthykun/smilelog",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
		"Programming Language :: Python :: 3.10",
        	"License :: OSI Approved :: MIT License",
        	"Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        'async-timeout>=4.0.2',
        'Deprecated>=1.2.13',
        'packaging>=21.3',
        'pyparsing>=3.0.9',
        'redis>=4.3.1',
        'wrapt>=1.14.1'
    ],
)
