from os import path

from setuptools import setup

INSTALL_REQUIRES = [
    'requests>=2.22.0',
    'urllib3',
    'plogger>=1.0.6'
]

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='pyrestclient',
      version='1.1.5',
      packages=['pyrestclient'],
      url='https://github.com/c-pher/RESTClient.git',
      license='MIT',
      author='Andrey Komissarov',
      author_email='a.komisssarov@gmail.com',
      description='The simple http client and REST test tool for humans.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=[
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Programming Language :: Python :: 3.6',
          'Topic :: System :: Systems Administration',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      install_requires=INSTALL_REQUIRES,
      python_requires='>=3.6',
      )
