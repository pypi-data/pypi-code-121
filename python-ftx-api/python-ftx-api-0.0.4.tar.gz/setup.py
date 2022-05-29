from __future__ import print_function
from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(
    name="python-ftx-api",
    version="0.0.4",
    packages=["pyftx"],
    description="FTX python wrapper with rest API, websocket API.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://gitlab.com/cuongitl/python-ftx-api",
    author="Cuongitl",
    author_email='',
    license="MIT",
    install_requires=["requests", "aiohttp", "websockets", "loguru"],
    keywords='Cuongitl ftx api restapi websocketapi example-python-ftx',
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
