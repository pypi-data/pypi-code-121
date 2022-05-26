"""
it4ifree setup
"""

import os
import platform

from setuptools import setup, find_packages

if 'IT4I_FACTORY_PREBUILD' in os.environ and os.environ['IT4I_FACTORY_PREBUILD']:
    SETUP_KWARGS = {'setup_requires': ['mustache',
                                       'pystache==0.5.4',
                                       'setuptools-git-version',
                                       'setuptools-markdown',
                                       'pypandoc'],
                    'version_format': '{tag}',
                    'long_description_markdown_filename': 'README.md'}
else:
    from version import version  # pylint: disable=import-error
    SETUP_KWARGS = {'setup_requires': [],
                    'version': version}

PLATFORM_FULLINFO = platform.platform()
DF_PREFIX = '' if 'ubuntu'.lower() in PLATFORM_FULLINFO.lower() else 'local/'

setup(name='it4i.portal.clients',
      description='Client tools for accessing various client APIs of IT4I portals',
      classifiers=[
          "Programming Language :: Python",
      ],
      keywords="""
accounting api client extranet feed it4i it4innovations it4i.portal.clients it4i-portal-clients \
motd pbs portal rss tool""",
      author='IT4Innovations',
      author_email='support@it4i.cz',
      url='http://www.it4i.cz/',
      license='BSD',
      packages=find_packages(),
      data_files=[('%setc/it4i-portal-clients/' % (DF_PREFIX),
                   ['it4i/portal/clients/templates/it4imotd.pt-sample',
                    'it4i/portal/clients/conf/main.cfg-sample'])],
      namespace_packages=['it4i', 'it4i.portal'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'ConfigParser',
          'argparse',
          'beautifulsoup4',
          'chameleon',
          'humanize',
          'lxml',
          'pycent',
          'python-dateutil',
          'simplejson',
          'tabulate',
      ],
      entry_points={
          'console_scripts': ['it4icheckaccess = it4i.portal.clients.it4icheckaccess:main',
                              'it4idedicatedtime = it4i.portal.clients.it4idedicatedtime:main',
                              'it4ifree = it4i.portal.clients.it4ifree:main',
                              'it4ifsusage = it4i.portal.clients.it4ifsusage:main',
                              'it4iuserfsusage = it4i.portal.clients.it4iuserfsusage:main',
                              'it4iprojectfsusage = it4i.portal.clients.it4iprojectfsusage:main',
                              'it4imotd = it4i.portal.clients.it4imotd:main']
      },
      **SETUP_KWARGS)
