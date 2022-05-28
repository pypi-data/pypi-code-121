from __future__ import print_function
from setuptools import setup

setup(
    name="python-ftx-api",
    version="0.0.1",
    packages=["pyftx"],
    description="FTX python wrapper with rest API, websocket API.",
    long_description="README.md",
    long_description_content_type="text/x-rst",
    url="https://gitlab.com/cuongitl/python-ftx-api",
    author="Cuongitl",
    author_email='',
    license="MIT",
    install_requires=["requests", "aiohttp", "websockets", "loguru"],
    keywords='ftx exchange rest api websocket example bitcoin ethereum btc eth neo',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    zip_safe=True,
)
