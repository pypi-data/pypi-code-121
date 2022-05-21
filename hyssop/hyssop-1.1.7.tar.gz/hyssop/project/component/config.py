# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: November 21st 2020

Modified By: hsky77
Last Updated: November 21st 2020 21:35:07 pm
'''

from ..constants import Component_Module_Folder
from ..config_validator import ConfigContainerMeta, ConfigElementMeta, ConfigScalableElementMeta, ProjectConfigValidator


ConfigComponentValidator = ConfigContainerMeta(
    Component_Module_Folder, False,
    ConfigContainerMeta(
        'localization', False,
        ConfigElementMeta('dir', str, False),
        ConfigElementMeta('lang', str, False)
    ),
    ConfigContainerMeta(
        'logger', False,
        ConfigElementMeta('dir', str, False)
    ),
    ConfigContainerMeta(
        'executor', False,
        ConfigElementMeta('worker_count', int, True)
    )
)

ProjectConfigValidator.set_cls_parameters(ConfigComponentValidator)
