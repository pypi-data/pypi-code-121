#
# This file is part of the python-openocd project.
#
# Copyright (C) 2020-2021 Marc Schink <dev@zapb.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import setuptools

with open('README.md', 'r') as fd:
    long_description = fd.read()

setuptools.setup(
    name='openocd',
    version='0.1.1',
    description='Python interface library for OpenOCD',
    long_description=long_description,
    keywords='OpenOCD',
    long_description_content_type='text/markdown',
    author='Marc Schink',
    author_email='dev@zapb.de',
    url='https://gitlab.zapb.de/openocd/python-openocd',
    license='GPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Embedded Systems',
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires='>=3.6',
)
