import io
import os
import sys
from shutil import rmtree

import nacos
from setuptools import Command, find_packages, setup

#  just run `python setup.py upload`
here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='UTF-8') as f:
    long_description = '\n' + f.read()


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds...')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution...')
        os.system(
            '{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine...')
        os.system('twine upload dist/*')

        sys.exit()


setup(
    name="nacos-client-py",
    version='0.0.4',
    packages=find_packages(
        exclude=["test", "*.tests", "*.tests.*", "tests.*", "tests"]),
    license="Apache License 2.0",
    python_requires='>=3.6',
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords=['nacos-client-py'],
    author='rencanwei',
    author_email="rencanwei@58.com",
    description="Python client for Nacos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'nacos-sdk-python==0.1.7',
        'requests==2.27.1'
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
