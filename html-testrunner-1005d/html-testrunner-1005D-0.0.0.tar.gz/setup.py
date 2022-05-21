#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

requirements = [
    # Package requirements here
    "Jinja2>=2.10.1"
]

test_requirements = [
    # Package test requirements here
]

setup(
    name='html-testrunner-1005D',
    description="A Test Runner in python, for Human Readable HTML Reports",
    long_description=__doc__,
    author="Ordanis Sanchez Suero",
    author_email='ordanisanchez@gmail.com',
    url='https://github.com/moderouin/HtmlTestRunner-1005D',
    packages=[
        'HtmlTestRunner',
    ],
    package_dir={'HtmlTestRunner':
                 'HtmlTestRunner'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='HtmlTestRunner TestRunner Html Reports',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
