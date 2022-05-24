import setuptools
from setuptools import setup, find_packages


setup(
    name='humingbird',
    version='0.2',
    description='Official Open Source version of Humingbird for Python',
    long_description='Please visit https://humingbird.co/docs for more info and documentation.',
    install_requires=[
             'Pillow>=7.1',
             'transformers>=4.19.2',
             'torch>=1.11.0'       
    ],
    license='MIT',
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"}
)


