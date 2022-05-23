# Copyright 2015-2020 Facundo Batista, Nicolás Demarchi
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  https://github.com/PyAr/fades

"""A module to package and viceversa conversion DB.

This is needed for names which don't match with the distrbution's name.
"""

MODULE_TO_PACKAGE = {
    'bs4': 'beautifulsoup4',
    'github3': 'github3.py',
    'uritemplate': 'uritemplate.py',
    'postgresql': 'py-postgresql',
    'yaml': 'pyyaml',
    'PIL': 'pillow',
    'Crypto': 'pycrypto',
}

PACKAGE_TO_MODULE = {v: k for k, v in MODULE_TO_PACKAGE.items()}
