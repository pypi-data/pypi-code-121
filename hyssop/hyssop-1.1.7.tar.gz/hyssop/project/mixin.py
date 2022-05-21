# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: November 21st 2020

Modified By: hsky77
Last Updated: March 3rd 2021 16:53:19 pm
'''


import os

from ..util import join_path, join_to_abs_path, BaseLocal
from .component import ComponentManager, ComponentTypes, create_component_manager
from .constants import Component_Module_Folder, LocalCode_File_Not_Found, Project_Config_File


class ProjectMixin():
    @property
    def project_dir(self) -> str:
        return self._project_dir

    @property
    def project_config_path(self) -> str:
        return join_to_abs_path(self.project_dir, Project_Config_File)

    @property
    def project_config(self):
        return self._project_config

    @property
    def component_manager(self) -> ComponentManager:
        return self._component_manager

    @property
    def name(self) -> str:
        return self.project_config['name']

    @property
    def debug(self) -> bool:
        return self.project_config['debug']

    def load_project(self, project_dir: str) -> None:
        self._project_dir = join_to_abs_path(project_dir)
        self._project_config = {}
        self._component_manager = None

        with open(self.project_config_path, 'r', encoding='utf8') as f:
            import yaml
            from .config_validator import ProjectConfigValidator
            validator = ProjectConfigValidator(
                yaml.load(f, Loader=yaml.SafeLoader))
            self._project_config = validator.parameter

        self._component_manager = create_component_manager(
            self.project_dir, self.project_config[Component_Module_Folder]) if Component_Module_Folder in self.project_config else create_component_manager(self.project_dir)
