#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
"PFAS_SAT_InputData",
"PFAS_SAT_ProcessModels",
"jupyter",
"pandas",
"stats-arrays",
"PySide2==5.14",
"plotly",
"graphviz",
"matplotlib",
"seaborn"
]

setup_requirements = [ ]

package_input_data = {'PFAS_SAT.html': ['*'],
                      'PFAS_SAT.html._images': ['*'],
                      'PFAS_SAT.html._sources': ['*'],
                      'PFAS_SAT.html._sources.Notebooks': ['*'],
                      'PFAS_SAT.html._static': ['*'],
                      'PFAS_SAT.html.Notebooks': ['*'],
                        }

test_requirements = [ ]

files = None


setup(
    author="Mojtaba Sardarmehni",
    author_email='msardar2@ncsu.edu',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
        'Natural Language :: English',
    ],
    description="Perfluoroalkyl Substances Systems Analysis Tool (PFAS_SAT)",
    install_requires=requirements,
    license="GNU GENERAL PUBLIC LICENSE V2",
    long_description=readme,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords='PFAS_SAT',
    name='PFAS_SAT',
    packages=find_packages(include=['PFAS_SAT', 'PFAS_SAT.*']),
    setup_requires=setup_requirements,
    package_data=package_input_data,
    data_files = files,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/PFAS-SAT/PFAS-SAT',
    version='0.3.1',
    zip_safe=False,
)
