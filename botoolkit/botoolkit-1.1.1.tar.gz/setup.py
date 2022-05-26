from codecs import (
    open,
)
from os import (
    path,
)

from setuptools import (
    find_packages,
    setup,
)

from botoolkit.settings import (
    ENTRY_POINTS,
)


PROJECT = 'botoolkit'

VERSION = '1.1.1'


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'CHANGES.md'), encoding='utf-8') as f:
    long_description += f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [
    x.strip()
    for x in all_reqs if
    'git+' not in x
]
dependency_links = [
    x.strip().replace('git+', '')
    for x in all_reqs if
    x.startswith('git+')
]

setup(
    name=PROJECT,
    version=VERSION,

    description='BO toolkit',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Alexander Danilenko',
    author_email='a.danilenko@bars.group',

    url='',
    download_url='',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Developers',
        'Environment :: Console',
    ],

    platforms=['Any'],

    scripts=[],

    provides=[],

    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    package_data={
        '': [
            '*.conf',
            '*.tmpl',
            '*.sh',
            'Dockerfile',
            '*.yaml',
        ],
    },

    install_requires=install_requires,
    dependency_links=dependency_links,

    entry_points=ENTRY_POINTS,

    zip_safe=False,
)
