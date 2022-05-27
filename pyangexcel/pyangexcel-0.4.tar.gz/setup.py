import os
from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='pyangexcel',
    version='0.4',
    description=('A pyang excel plugin to produce a Excel Schema file'),
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    packages=['pyangexcel'],
    author='neoul',
    author_email='neoul@ymail.com',
    license='Apache License',
    url='https://github.com/neoul/pyangexcel',
    install_requires=['pyang', 'openpyxl'],
    include_package_data=True,
    keywords=['pyang', 'yang'],
    zip_safe=False,
    classifiers=[],
)
