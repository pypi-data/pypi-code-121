from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'DrawioParser'
LONG_DESCRIPTION = 'DrawioParser'

# Setting up
setup(
    name="colelmen_drawio_parser",
    version=VERSION,
    author="Colemen Atwood",
    author_email="<atwoodcolemen@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    py_modules=[
        'utils.objectUtils',
        'utils.diagramUtils',
        'connector',
        'diagram',
        'drawing',
        'main',
        'mxcell',
        'nodeBase',
        'onode',
    ],
    # add any additional packages that
    # need to be installed along with your package. Eg: 'caer'
    install_requires=[
        'colemen_file_utils',
        'colemen_string_utils',
        'lxml',
    ],

    keywords=['python'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
