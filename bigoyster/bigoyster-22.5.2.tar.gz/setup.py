from setuptools import setup
import os

setup(
    name='bigoyster',
    packages=['bigoyster'],
    version="22.5.2",
    license='MIT',
    description='Python wrapper for Deals Media API',
    long_description='Python wrapper for Deals Media API',
    long_description_content_type='text/markdown',
    author='Mark Meadows',
    author_email='mark@mvmdata.com',
    url='https://gitlab.com/mvmdata/bigoyster',
    keywords=['Big Oyster', 'python', 'Petzmobile', 'coupons'],
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
