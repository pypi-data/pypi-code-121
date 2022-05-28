import codecs
from pathlib import (
    Path,
)

from setuptools import (
    find_packages,
)

from m3_gar.version import (
    __version__,
)


def read(fn):
    return codecs.open(Path(__file__).resolve().parent / fn).read()


def make_setup_kwargs():
    return dict(
        name='m3-gar',
        version=__version__,
        author='BARS Group',
        author_email='bars@bars.group',
        description='GAR Django integration for m3',
        long_description=read('README.rst'),
        license='MIT license',
        install_requires=[
            'Django>=3.2',
            'requests',
            'lxml',
            'progress',
            'gitpython',
            'twine',
            'asyncpg',
            'uvloop',
            'django-cte==1.1.5',
            'm3-gar-constants==1.0.3',
        ],
        packages=find_packages(exclude=['tests', 'test_project']),
        include_package_data=True,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: Russian',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.9',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
