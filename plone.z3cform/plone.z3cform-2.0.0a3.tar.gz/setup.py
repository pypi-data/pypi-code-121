from setuptools import setup, find_packages

import os

__version__ = '2.0.0a3'


def description():
    join = lambda *paths: os.path.join('src', 'plone', 'z3cform', *paths)
    return (
        open('README.rst').read()
        + '\n'
        + open(join('fieldsets', 'README.rst')).read()
        + '\n'
        + open(join('crud', 'README.txt')).read()
        + '\n'
        + open('CHANGES.rst').read()
        + '\n'
    )


setup(
    name='plone.z3cform',
    version=__version__,
    description='plone.z3cform is a library that allows use of z3c.form '
    'with Zope and the CMF.',
    long_description=description(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords='Plone CMF Python Zope CMS Webapplication',
    author='Plone Foundation',
    author_email='releasemanager@plone.org',
    url='https://github.com/plone/plone.z3cform',
    license='GPL version 2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'plone.batching',
        'six',
        'z3c.form>=4.0',
        'zope.i18n>=3.4',
        'zope.browserpage',
        'zope.component',
        'Zope',
    ],
    extras_require={'test': ['lxml', 'plone.testing[z2]']},
)
