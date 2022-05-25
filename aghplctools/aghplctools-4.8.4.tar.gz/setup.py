import aghplctools
from setuptools import setup, find_packages

NAME = 'aghplctools'
AUTHOR = 'Lars Yunker / Hein Group'

PACKAGES = find_packages()
# KEYWORDS = ', '.join([
# ])

with open('LICENSE') as f:
    lic = f.read()
    lic.replace('\n', ' ')

# with open('README.MD') as f:
#     long_description = f.read()

setup(
    name=NAME,
    version=aghplctools.__version__,
    description='Interaction package for Agilent ChemStation report files',
    # long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    url='https://gitlab.com/heingroup/aghplctools',
    packages=PACKAGES,
    license=lic,
    python_requires='>=3.8',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Operating System :: Microsoft :: Windows',
        'Natural Language :: English'
    ],
    project_urls={
        'Documentation': 'https://aghplctools.readthedocs.io/en/latest/',
        'Hein Group': 'https://groups.chem.ubc.ca/jheints1/',
    },
    # keywords=KEYWORDS,
    install_requires=[
        'numpy',
        'matplotlib>=3.0.3',
        'tqdm',
        'unithandler>=1.3.3',
        'openpyxl>=2.6.2',
        'hein_utilities>=3.5',
        'aston>=0.7.0',
    ],
)
