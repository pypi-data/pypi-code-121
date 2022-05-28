import os
import setuptools
from distutils.core import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


REQUIRED = ['pyparsing']

BIN_DIR = os.path.dirname(os.path.realpath(__file__))

EXTRAS = {
}

setup(
    name='paddl',
    version='0.1.2',  # open("VERSION", "r").read(),
    packages=setuptools.find_packages(),
    # ['telemetry',],
    package_data={'': ['README.md', 'VERSION']},
    #package_dir={ 'telemetry': 'src/telemetry' },
    description="Parse Any DDL",
    # long_description=open('README2.0.md').read(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='trevor grayson',
    author_email='trevor@dave.com',
    url='http://github.com/trevorgrayson/paddl',

    py_modules=['paddl'],
    scripts=[],
    # entry_points={ },

    # python_requires='2.7', #todo
    # install_requires=REQUIRED,
    extras_require=EXTRAS,
    # include_package_data=True,
    license='MIT',
    classifiers=[
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 4',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Logging',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.6',
        # 'Programming Language :: Python :: Implementation :: CPython',
        # 'Programming Language :: Python :: Implementation :: PyPy'
    ],
    include_package_data=True
)

# https://github.com/kennethreitz/setup.py/blob/master/setup.py
