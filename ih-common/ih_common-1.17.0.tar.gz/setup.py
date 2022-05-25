import setuptools
from setuptools import setup
with open("README.md", "r") as fh:
    long_description = fh.read()

setup (
    name = 'ih_common',
    version = '1.17.0',
    author = 'hanchuanjun',
    author_email = 'han@inhand.com.cn',
    url = 'https://gitlab.inhand.design/hancj-dev/py-common',
    description = 'tool',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires=[
        'pika',
        'urllib3',
        'python-consul'
	],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)