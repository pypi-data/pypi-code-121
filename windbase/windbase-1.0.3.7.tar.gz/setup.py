#!/usr/bin/env python3
# coding=utf-8

from setuptools import find_packages, setup
import sys

buildno = 1
try:
    with open("./buildno","r") as fp:
        buildno = int(fp.readline())
except:
    pass
if sys.argv[1]=="sdist":
    try:
        with open("./buildno","w") as fp:
            buildno += 1
            fp.write(str(buildno))
    except:
        pass

setup(name='windbase',
      author='gonewind.he',
      author_email='gonewind.he@gmail.com',
      maintainer='gonewind',
      maintainer_email='gonewind.he@gmail.com',
      url='https://github.com/gonewind73/wind_util',
      description='windbase in python',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      version='1.0.3.'+str(buildno),
      python_requires='>=3',
      platforms=["Linux", "Windows"],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Networking'],
      packages=find_packages(include=['windbase']),
      data_files=[
        # ('destdir', ['srcdirfile']),
        ('', ['README.md','requirements.txt',"buildno"]),
               ],
      entry_points={
          'console_scripts': [
              'admin_lite = windbase.adminlite:main',
          ]
      },
      )
