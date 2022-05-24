"""Packaging dgspoc."""

from setuptools import setup, find_packages


setup(
    name='dgspoc',
    version='0.3.7',
    license='BSD-3-Clause',
    license_files=['LICENSE'],
    description='The proof of concept for Describe-Get-System.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Tuyen Mathew Duong',
    author_email='tuyen@geekstrident.com',
    maintainer='Tuyen Mathew Duong',
    maintainer_email='tuyen@geekstrident.com',
    install_requires=[
        'compare_versions',
        'python-dateutil',
        'textfsm',
        'pyyaml',
        'pytest',
        'robotframework',
        'dlapp',
        'regexapp',
        'templateapp',
        'gtunrealdevice',
        'unittest-xml-reporting'
    ],
    url='https://github.com/Geeks-Trident-LLC/dgspoc',
    packages=find_packages(
        exclude=(
            'tests*', 'testing*', 'examples*',
            'build*', 'dist*', 'docs*', 'venv*'
        )
    ),
    include_package_data=True,
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'dgs = dgspoc.main:execute',
            'dgspoc = dgspoc.main:execute',
        ]
    },
    classifiers=[
        # development status
        'Development Status :: 2 - Pre-Alpha',
        # natural language
        'Natural Language :: English',
        # intended audience
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        # operating system
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        # license
        'License :: OSI Approved :: BSD License',
        # programming language
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        # topic
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Scientific/Engineering',
        'Topic :: Text Processing',
    ],
)
