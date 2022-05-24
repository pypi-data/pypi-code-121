"""Module containing the attributes for describe-get-system proof of concept module."""

from os import path
from textwrap import dedent
import yaml

import templateapp
import regexapp
import dlapp

import pytest
import robot
import xmlrunner

from dgspoc.utils import File
from dgspoc.utils import Misc

__version__ = '0.3.7'
version = __version__

__all__ = [
    'version',
    'Data'
]


class Data:

    console_cli_name = 'dgs'
    console_cli_fullname = 'describe-get-system'
    console_supported_commands = ['build', 'info', 'report', 'search',
                                  'test', 'version', 'usage']

    # app yaml files
    app_directory = File.get_path('.geekstrident', 'dgspoc', is_home=True)
    template_storage_filename = File.get_path(app_directory, 'template_storage.yaml')

    # main app
    main_app_text = 'dgs v{}'.format(version)

    # company
    company = 'Geeks Trident LLC'
    company_url = 'https://www.geekstrident.com/'

    # URL
    repo_url = 'https://github.com/Geeks-Trident-LLC/dgspoc'
    # TODO: Need to update wiki page for documentation_url instead of README.md.
    documentation_url = path.join(repo_url, 'blob/develop/README.md')
    license_url = path.join(repo_url, 'blob/develop/LICENSE')

    # License
    years = '2022-2040'
    license_name = 'BSD 3-Clause License'
    copyright_text = 'Copyright @ {}'.format(years)
    license = dedent(
        """
        BSD 3-Clause License

        Copyright (c) {}, {}
        All rights reserved.

        Redistribution and use in source and binary forms, with or without
        modification, are permitted provided that the following conditions are met:

        1. Redistributions of source code must retain the above copyright notice, this
           list of conditions and the following disclaimer.

        2. Redistributions in binary form must reproduce the above copyright notice,
           this list of conditions and the following disclaimer in the documentation
           and/or other materials provided with the distribution.

        3. Neither the name of the copyright holder nor the names of its
           contributors may be used to endorse or promote products derived from
           this software without specific prior written permission.

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
        AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
        IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
        DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
        FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
        DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
        SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
        CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
        OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
        OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
        """.format(years, company)
    ).strip()

    @classmethod
    def get_app_info(cls):
        from platform import uname as u, python_version as v
        lst = [cls.main_app_text,
               'Project : {}'.format(cls.repo_url),
               'License : {}'.format(cls.license_name),
               'Platform: {0.system} {0.release} - Python {1}'.format(u(), v()),
               ]
        app_info = '\n'.join(lst)
        return app_info

    @classmethod
    def get_dependency(cls):
        obj = dict(
            templateapp=dict(
                package='templateapp v{}'.format(templateapp.version),
                url='https://pypi.org/project/templateapp/'
            ),
            pytest=dict(
                package='pytest v{}'.format(pytest.__version__),
                url='https://pypi.org/project/pytest/'
            ),
            robotframework=dict(
                package='robotframework v{}'.format(robot.__version__),
                url='https://pypi.org/project/robotframework/'
            ),
            unittest_xml_reporting=dict(
                package='unittest-xml-reporting v{}'.format(xmlrunner.__version__),
                url='https://pypi.org/project/unittest-xml-reporting/'
            )
        )
        obj.update(templateapp.config.Data.get_dependency())
        obj.update(regexapp.config.Data.get_dependency())
        obj.update(dlapp.config.Data.get_dependency())
        dependencies = dict(sorted(obj.items(), key=lambda x: str(x[0])))   # noqa
        return dependencies

    @classmethod
    def get_template_storage_info(cls):
        fn = cls.template_storage_filename
        generic_fn = File.change_home_dir_to_generic(fn)
        if File.is_exist(fn):
            existed = 'Yes'
            with open(fn) as stream:
                node = yaml.safe_load(stream)
                total = len(node) if Misc.is_dict(node) else 0
        else:
            existed = 'No'
            total = 0
        lst = [
            'Template Storage Info:',
            # '  - Location: {}'.format(fn),
            '  - Location: {}'.format(generic_fn),
            '  - Existed: {}'.format(existed),
            '  - Total Templates: {}'.format(total)
        ]
        return '\n'.join(lst)
