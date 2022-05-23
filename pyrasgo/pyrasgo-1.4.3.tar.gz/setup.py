from setuptools import setup
import os

_here = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(os.path.join(_here, 'pyrasgo', 'version.py')) as f:
    exec(f.read(), version)

with open(os.path.join(_here, 'DESCRIPTION.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyrasgo',
    version=version['__version__'],
    description='Python interface to the Rasgo API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Patrick Dougherty',
    author_email='patrick@rasgoml.com',
    url='https://www.rasgoml.com/',
    license='GNU Affero General Public License v3 or later (AGPLv3+)',
    project_urls={
        'Documentation': 'https://docs.rasgoml.com',
        'Source': 'https://github.com/rasgointelligence/RasgoSDKPython',
        'Rasgo': 'https://www.rasgoml.com/',
        'Changelog': 'https://github.com/rasgointelligence/RasgoSDKPython/blob/master/pyrasgo/CHANGELOG.md',
    },
    packages=[
        'pyrasgo',
        'pyrasgo.api',
        'pyrasgo.primitives',
        'pyrasgo.schemas',
        'pyrasgo.storage',
        'pyrasgo.storage.dataframe',
        'pyrasgo.storage.datawarehouse',
        'pyrasgo.utils',
    ],
    install_requires=[
        # Note these are duplicated in requirements.txt
        "more-itertools",
        "pandas",
        "pydantic",
        "pyyaml",
        "requests",
        "snowflake-connector-python>=2.7.1",
        "snowflake-connector-python[pandas]",
        "typing_extensions",
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
)
