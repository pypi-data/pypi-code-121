"""Setup for mercurial_update_version."""

from setuptools import setup

VERSION = '1.2.0'
LONG_DESCRIPTION = open("README.rst").read()
INSTALL_REQUIRES = [
    "mercurial_extension_utils>=1.5.0",
]

setup(
    name="mercurial_update_version",
    version=VERSION,
    author='Marcin Kasperski',
    author_email='Marcin.Kasperski@mekk.waw.pl',
    url='https://foss.heptapod.net/mercurial/mercurial-update_version',
    description='Mercurial Update Version Extension',
    long_description=LONG_DESCRIPTION,
    license='BSD',
    py_modules=[
        'mercurial_update_version',
    ],
    install_requires=INSTALL_REQUIRES,
    keywords="mercurial hg version auto-update tag",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: DFSG approved',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Version Control'
    ],
    zip_safe=True)
