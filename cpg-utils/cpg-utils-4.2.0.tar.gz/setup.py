#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='cpg-utils',
    # This tag is automatically updated by bumpversion
    version='4.2.0',
    description='Library of convenience functions specific to the CPG',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url=f'https://github.com/populationgenomics/cpg-utils',
    license='MIT',
    packages=['cpg_utils'],
    install_requires=[
        'google-auth',
        'google-cloud-secret-manager',
        'cloudpathlib[all]',
    ],
    include_package_data=True,
    keywords='bioinformatics',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
)
