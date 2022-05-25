# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.api.architecture_component import ArchitectureComponent


def append_db(context):
    """
    Add an Architecture Component to Activity
    for Teamserver to display database usage.
    """
    if not context.database_info:
        return

    for db_info in context.database_info:
        arch_comp = ArchitectureComponent(db_info).to_dtm()
        context.activity.architectures.extend([arch_comp])
