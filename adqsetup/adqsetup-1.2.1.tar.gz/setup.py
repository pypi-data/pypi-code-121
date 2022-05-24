import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='adqsetup',
    version='1.2.1',
    description='A pure Python tool and library to setup ADQ for Intel NICs',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',    
    url='https://www.intel.com/content/www/us/en/architecture-and-technology/ethernet/adq-resource-center.html',
    author='Intel',
    license='BSD-3-Clause',
    py_modules=['adqsetup'],
    entry_points={
        'console_scripts': [
            'adqsetup=adqsetup:_main',
        ]
    },
    zip_safe=False
)
