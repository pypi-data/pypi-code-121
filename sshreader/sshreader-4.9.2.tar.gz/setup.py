#!/usr/bin/env python3
# coding=utf-8
"""Setup file for sshreader module"""

from setuptools import setup


setup(name='sshreader',
      version='4.9.2',
      description='Multi-threading/processing wrapper for Paramiko',
      author='Jesse Almanrode',
      author_email='jesse@almanrode.com',
      url='http://sshreader.readthedocs.io/',
      project_urls={'Documentation': 'http://sshreader.readthedocs.io/',
                    'Source': 'https://bitbucket.org/isaiah1112/sshreader/',
                    'Tracker': 'https://bitbucket.org/isaiah1112/sshreader/issues'},
      packages=['sshreader'],
      include_package_data=True,
      scripts=['bin/pydsh'],
      install_requires=['click>=8.0.3',
                        'colorama>=0.4.4',
                        'paramiko>=2.11.0',
                        'progressbar2>=3.55.0',
                        'python-hostlist>=1.21',
                        ],
      platforms=['Linux', 'Darwin'],
      classifiers=[
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      )
