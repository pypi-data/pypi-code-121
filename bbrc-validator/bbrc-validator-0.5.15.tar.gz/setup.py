from setuptools import setup, find_packages
from glob import glob
import os.path as op


version = '0.5.15'

requirements = ['coverage>=4.5',
                'dateparser>=0.7',
                'lxml>=4.3',
                'Markdown>=3.0',
                'nibabel>=2.3',
                'nilearn>=0.5',
                'nose>=1.3',
                'numpy>=1.16',
                'pandas>=0.24',
                'pdfkit>=0.6',
                'pydicom>=2.0',
                'requests>=2.21',
                'scikit-image>=0.14',
                'scikit-learn>=0.2',
                'scipy>=1.2',
                'xlrd>=1.2',
                'xlutils>=2',
                'xlwt>=1.3',
                'bbrc-pyxnat>=1.4.2',
                'pytz>=2019.1',
                'nisnap==0.4.post0',
                'matplotlib',
                'tqdm>=4.50']

description = 'Systematic sanity checks on imaging datasets within an XNAT '\
    'environment'

download_url = 'https://gitlab.com/bbrc/xnat/bbrc-validator/-/archive/'\
    'v{v}/bbrc-validator-v{v}.tar.gz'.format(v=version)

this_directory = op.abspath(op.dirname(__file__))
with open(op.join(this_directory, 'README.md'), 'r') as f:
    long_description = f.read()

setup(
    name='bbrc-validator',
    packages=find_packages(exclude='tests'),
    install_requires=requirements,
    version=version,
    package_data={'bbrc': ['data/*', 'data/**/*']},
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Greg Operto, Jordi Huguet',
    author_email='goperto@barcelonabeta.org',
    url='https://gitlab.com/bbrc/xnat/bbrc-validator',
    download_url=download_url,
    classifiers=['Intended Audience :: Science/Research',
                 'Intended Audience :: Developers',
                 'Topic :: Scientific/Engineering',
                 'Operating System :: Unix',
                 'Programming Language :: Python :: 3.7'],
    scripts=glob(op.join('bin', '*'))
)
