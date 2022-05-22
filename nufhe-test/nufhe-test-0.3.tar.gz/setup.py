# Copyright (C) 2018 NuCypher
#
# This file is part of nufhe.
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from setuptools import setup

setup(
    name='nufhe-test',
    version='0.3',
    description='testing',
    url='http://github.com/pradeep508',
    author='pradeep',
    author_email='pradeepkumarreddy.bukka@gmail.com',
    license='GPLv3',
    packages=[
        'nufhe_test',
        'nufhe_test/transform',
        ],
    package_data={
        'nufhe_test': ['*.mako'],
        'nufhe_test/transform': ['*.mako'],
        },
    install_requires=['numpy', 'reikna>=0.7.5'],
    python_requires='>=3.5',
    extras_require={
        'dev': ['pytest', 'pytest-cov', 'sphinx', 'sphinx_autodoc_typehints'],
        'pyopencl': ['pyopencl>=2018.1.1'],
        'pycuda': ['pycuda>=2018.1.1'],
        },
    zip_safe=True)
