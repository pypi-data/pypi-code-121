from setuptools import setup, find_packages

import hashboard
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), 'r') as f:
    long_description = f.read()

setup(
    name='hashboard',
    version=hashboard.__version__,
    description='Tool for estimating the profitability of bitcoin ASICs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Adam P. Goucher',
    author_email='adam@hatsya.com',
    url='https://gitlab.com/apgoucher/hashboard',
    license='MIT',
    packages=['hashboard'],
    # test_suite='lifelib.tests',
    include_package_data=True,
    zip_safe=False,
    install_requires=['numpy>=1.13', 'pandas>=1.3', 'scikit-learn>=1.0', 'seaborn>=0.11', 'scipy>=1.7', 'dateparser>=1.1'],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',

        # MIT licence as always:
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.8',

        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics',
    ])
