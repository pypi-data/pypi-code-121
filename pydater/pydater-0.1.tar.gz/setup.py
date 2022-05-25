from setuptools import setup,find_packages

classifiers = [
    "Operating System :: Microsoft :: Windows :: Windows 10",
    "Programming Language :: Python :: 3.9"
]

setup(
    name='pydater',
    description='Basic program or file updater',
    version='0.1',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Helmsys',
    author_email='arif.c20e@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords=['update','auto update','updater'],
    packages=find_packages(),
    install_requires=['requests'])