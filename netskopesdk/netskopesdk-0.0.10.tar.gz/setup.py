import setuptools
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="netskopesdk",
    version="0.0.10",
    author="Bharath Rajendran",
    author_email="bharath@netskope.com",
    description="SDK to download the Netskope Events",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.netskope.com/",
    project_urls={
        "Bug Tracker": "http://www.netskope.com/",
    },

    include_package_data = True,

    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    package_dir = { '' : 'src' },
    packages    = find_packages(where='src'),

    python_requires=">=3.6",

    install_requires = [
        "requests==2.27.1"
    ]
)
