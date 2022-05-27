from setuptools import setup
from setuptools import find_packages

with open("README.rst", "r") as f:
    long_description = f.read()

setup(
    name='MLplayground',              # package name
    version='1.0.0',            # package version
    description='A mini Machine Learning Algorithm Library',
    long_description=long_description,
    author='LujiaZhong',
    url='https://lujiazho.github.io/',
    install_requires=[
        "numpy==1.21.1",
        "matplotlib==3.5.1"
    ],
    license='MIT License',
    packages=find_packages(),
    platforms=["Windows 10"],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
)