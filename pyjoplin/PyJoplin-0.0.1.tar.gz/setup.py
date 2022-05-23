# -*- coding: utf-8 -*-

from os.path import abspath, dirname, exists, join

from setuptools import find_packages, setup

long_description = None
if exists("README.rst"):
    with  open("README.rst") as file:
        long_description = file.read()

install_reqs = [req
                for req in
                open(abspath(join(dirname(__file__), 'requirements.txt')))]

setup(
        name='PyJoplin',
        version="0.0.1",
        description="A Python interface of Joplin.",
        long_description_content_type="text/x-rst",
        long_description=long_description,
        author='songs18',
        author_email='songs18@example.com',
        license='MIT',
        packages=find_packages(),
        platforms=['all'],
        url="https://github.com/songs18/PyJoplin",
        zip_safe=False,
        include_package_data=True,
        install_requires=install_reqs,
        python_requires='>=3.5'
)
