#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='cpg-utils-ms',
    # This tag is automatically updated by bumpversion
    version='0.7.1',
    description='Library of convenience functions specific to the CPG (MS version)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url=f'https://github.com/gregsmi/cpg-utils',
    license='MIT',
    packages=['cpg_utils'],
    install_requires=[
        'google-auth',
        'google-cloud-secret-manager',
        'azure-identity',
        'azure-keyvault-secrets',
        'azure-storage-blob',
        'cloudpathlib[all]',
    ],
    python_requires=">=3.8",
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
