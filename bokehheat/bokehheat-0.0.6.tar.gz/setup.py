"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject

pip releasing a next version:
1. vim ./bokehheat/_version.py  # increase version number in file
2. git add ./bokehheat/_version.py
3. git commit -m'@ bokehheat : next version.'
4. git tag -a vn.o.p -m'version n.o.p'
5. python3 -m build --sdist  # make source distribution
6. python3 -m build --wheel  # make binary distribution python wheel
7. twine upload dist/* --verbose
8. git push origin master
9. git push --tag
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get the version number from the _version.py file
exec(open('./bokehheat/_version.py').read())

setup(
    # the basics
    name='bokehheat',
    version=__version__,

    # description
    description='A python3 bokeh based boolean data, categorical data, numerical data, dendrogram, and heatmap plotting library.',
    long_description=long_description,
    long_description_content_type='text/markdown',

    # the project's main homepage.
    url='https://gitlab.com/biotransistor/bokehheat',

    # author details
    author="Elmar Bucher",
    author_email="ulmusfagus@zoho.com",

    # the license
    license="GPL>=3",

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Visualization',

        # Pick your license as you wish
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='visualization bokeh dendrogram cladogram heatmap',

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=[]),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    python_requires='>=3.6',
    install_requires=['bokeh', 'matplotlib', 'pandas', 'scipy', 'selenium'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #   $ pip install sampleproject[dev]
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    #extras_require={  # Optional
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        "bokehheat": [
            "error.json",
        ],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('my_data', ['data/data_file'])],  # Optional

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #entry_points={  # Optional
    #    'console_scripts': [
    #        'sample=sample:main',
    #    ],
    #},

    # List additional URLs that are relevant to your project as a dict.
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    project_urls={
        'Bug Reports': 'https://gitlab.com/biotransistor/bokehheat/issues',
        'Funding': 'https://donate.doctorswithoutborders.org',
        #'Say Thanks!': 'http://saythanks.io/',
        'Source': 'https://gitlab.com/biotransistor/bokehheat/',
    },
)
