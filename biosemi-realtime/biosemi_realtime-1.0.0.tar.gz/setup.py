#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os


def run_setup():
    _folder = os.path.dirname(os.path.realpath(__file__))
    requirement_path = _folder + os.path.sep + 'requirements.txt'
    install_requires = []
    if os.path.isfile(requirement_path):
        with open(requirement_path) as f:
            install_requires = f.read().splitlines()
    version = open('VERSION').read()
    setup(name="biosemi_realtime",
          install_requires=install_requires,
          setup_requires=['gitpython'],
          version=version,
          packages=find_packages(),
          author="Jaime A. Undurraga",
          author_email="jaime.undurraga@gmail.com",
          description="This python package allows real-time averaging in the time- and frequency-domain with SNR"
                      " estimations.",
          long_description="""
          This package provides a real-time averager which allows time- and frequency-domain averages. Data are averaged
          via bayesian weighted average and SNR in the time and frequency domain are provided.  
          """,
          license="MIT",
          url="https://gitlab.com/jundurraga/biosemi_real_time",
          include_package_data=True,
          classifiers=[
              'Development Status :: 3 - Alpha',
              'Environment :: Console',
              'Intended Audience :: Science/Research',
              'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
              'Operating System :: MacOS :: MacOS X',
              'Operating System :: Microsoft :: Windows :: Windows 10',
              'Operating System :: POSIX :: Linux',
              'Programming Language :: Python :: 3',
              'Topic :: Scientific/Engineering :: Bio-Informatics'
              ]
          )
    update_git_hash_version()


def update_git_hash_version():
    """Return version with local version identifier."""
    import git
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    with open('GITHEADHASH', mode='w+') as f:
        f.write(sha)


if __name__ == '__main__':
    run_setup()
