# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: November 21st 2020

Modified By: hsky77
Last Updated: November 21st 2020 21:43:10 pm
'''

import os

from ...util import join_path, DynamicTypeEnum, join_to_abs_path, BaseLocal
from ..component import (ComponentManager, ComponentTypes,
                         DefaultComponentTypes, create_component_manager)
from ..constants import Component_Module_Folder, LocalCode_File_Not_Found, Project_Config_File
from ..mixin import ProjectMixin
from .controller import get_project_controllers


class WebApplicationMinin(ProjectMixin):
    @property
    def project_controllers(self):
        if not hasattr(self, '_project_controllers'):
            self._project_controllers = get_project_controllers(
                self.project_config, self.project_dir)

        return self._project_controllers

    @property
    def project_ssl_context(self):
        if 'ssl' in self.project_config:
            if not os.path.isfile(join_path(self.project_config['ssl']['crt'])):
                raise FileNotFoundError(BaseLocal.get_message(
                    LocalCode_File_Not_Found, join_path(self.project_config['ssl']['crt'])))
            if not os.path.isfile(join_path(self.project_config['ssl']['key'])):
                raise FileNotFoundError(BaseLocal.get_message(
                    LocalCode_File_Not_Found, join_path(self.project_config['ssl']['key'])))

            import ssl
            ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_ctx.load_cert_chain(join_path(self.project_config['ssl']['crt']),
                                    join_path(self.project_config['ssl']['key']))
            if 'ca' in self.project_config['ssl']:
                if not os.path.isfile(join_path(self.project_config['ssl']['ca'])):
                    raise FileNotFoundError(BaseLocal.get_message(
                        LocalCode_File_Not_Found, join_path(self.project_config['ssl']['ca'])))
                ssl_ctx.load_verify_locations(
                    join_path(self.project_config['ssl']['ca']))
            return ssl_ctx
