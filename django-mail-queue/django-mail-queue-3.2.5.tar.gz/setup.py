from setuptools import setup, find_packages

import mailqueue

version = mailqueue.VERSION

setup(name='django-mail-queue',
      version=version,
      description="Simple Mail Queuing for Django",
      long_description=open("README.md", "r").read(),
      long_description_content_type="text/markdown",
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
          "Topic :: Utilities",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Framework :: Django",
          "Framework :: Django :: 1.8",
          "Framework :: Django :: 1.9",
          "Framework :: Django :: 2.0",
          "Framework :: Django :: 2.1",
          "Framework :: Django :: 2.2",
          "License :: OSI Approved :: MIT License",
          ],
      keywords='django-mail-queue',
      author='Privex Inc. (2019+) / Derek Stegelman (2011-2018)',
      url='http://github.com/Privex/django-mail-queue',
      author_email='chris@privex.io',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
)
