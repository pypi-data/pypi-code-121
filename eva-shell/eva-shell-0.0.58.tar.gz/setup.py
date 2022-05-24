__version__ = '0.0.58'

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(name='eva-shell',
                 version=__version__,
                 author='Bohemia Automation / Altertech',
                 author_email='div@altertech.com',
                 description='EVA ICS v4 shell',
                 long_description=long_description,
                 long_description_content_type='text/markdown',
                 url='https://github.com/alttch/eva4',
                 packages=setuptools.find_packages(),
                 license='Apache License 2.0',
                 install_requires=[
                     'elbus>=0.0.14', 'evaics>=0.0.23', 'yedb[cli]>=0.2.22',
                     'argcomplete>=2.0.0', 'python-dateutil>=2.7.3',
                     'neotermcolor>=2.0.10', 'pyyaml>=6.0', 'pygments>=2.11.2',
                     'pytz>=2021.3', 'pwinput>=1.0.2'
                 ],
                 classifiers=('Programming Language :: Python :: 3',
                              'License :: OSI Approved :: MIT License',
                              'Topic :: Communications'),
                 scripts=['bin/eva'])
