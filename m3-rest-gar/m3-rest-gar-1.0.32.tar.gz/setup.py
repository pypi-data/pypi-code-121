import codecs
from pathlib import (
    Path,
)

from setuptools import (
    setup,
)


def read(fn):
    return codecs.open(Path(__file__).resolve().parent / fn).read()


setup(
    name='m3-rest-gar',
    version='1.0.32',
    description=("REST-service for GAR."),
    author='BARS Group',
    author_email='bars@bars.group',
    license="MIT",
    keywords="django rest gar",
    long_description=read('README.rst'),
    packages=['m3_rest_gar'],
    install_requires=read('requirements.txt'),
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ),
)
