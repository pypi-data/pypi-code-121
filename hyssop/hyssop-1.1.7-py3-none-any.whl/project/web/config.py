# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: November 21st 2020

Modified By: hsky77
Last Updated: November 21st 2020 21:34:57 pm
'''

from ..constants import Controller_Module_Folder
from ..config_validator import ConfigContainerMeta, ConfigElementMeta, ConfigScalableContainerMeta, ProjectConfigValidator

ProjectConfigValidator.set_cls_parameters(
    ConfigElementMeta('port', int, False))
ProjectConfigValidator.set_cls_parameters(ConfigContainerMeta(
    'ssl', False,
    ConfigElementMeta('crt', str, True),
    ConfigElementMeta('key', str, True),
    ConfigElementMeta('ca', str, False)
))


ConfigControllerValidator = ConfigContainerMeta(
    Controller_Module_Folder, False,
    ConfigScalableContainerMeta(
        str,
        ConfigElementMeta('enum', str, True),
        ConfigContainerMeta('params', False)
    )
)

ProjectConfigValidator.set_cls_parameters(ConfigControllerValidator)
