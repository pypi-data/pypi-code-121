import setuptools

setuptools.setup(
    name='iambcodes',
    version='0.0.19',
    author='Ulf Liebal',
    author_email='ulf.liebal@rwth-aachen.de',
    description='Functions for data analysis support at the iAMB in RWTH Aachen.',
    keywords='biolog',
    url='https://git.rwth-aachen.de/ulf.liebal/iambcodes',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    python_requires='>=3.6',
    install_requires=[
        'xlrd>=2.0.1',
        'numpy>=1.18.2',
        'cobra>=0.22.1',
        'biopython>=1.78',
        'matplotlib>=3.3.4',
        'scipy>=1.7.3',
    ],
)
