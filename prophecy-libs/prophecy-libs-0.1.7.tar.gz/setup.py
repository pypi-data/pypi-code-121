from setuptools import setup, find_packages

setup(
    name='prophecy-libs',
    version='0.1.7',
    url='https://github.com/SimpleDataLabsInc/prophecy-python-libs',
    packages=find_packages(exclude=['test.*', 'test']),
    description='Helper library for prophecy generated code',
    long_description=open('README.md').read(),
    install_requires=[
        'pyspark==3.2.0'
    ],
    keywords=['python', 'prophecy'],
    classifiers=[
    ],
    zip_safe=False
)
