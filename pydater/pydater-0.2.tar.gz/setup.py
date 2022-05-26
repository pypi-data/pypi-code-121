from setuptools import setup,find_packages

classifiers = [
    "Operating System :: Microsoft :: Windows :: Windows 10",
    "Programming Language :: Python :: 3.9"
]

setup(
    name='pydater',
    description='Basic program and file updater for Github',
    version='0.2',
    long_description=open('README.md',encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Arif-Helmsys",
    author='Helmsys',
    author_email='arif.c20e@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords=['update','auto update','updater'],
    packages=find_packages(),
    install_requires=['requests'])