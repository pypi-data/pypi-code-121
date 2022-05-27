# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio service to connect InvenioRDM to Alma."""

from .alma import AlmaRESTService, AlmaSRUService

# from .config import AlmaServiceConfig, RepositoryServiceConfig
# from .repository import RepositoryService

__all__ = (
    #    "AlmaServiceConfig",
    #    "RepositoryServiceConfig",
    "AlmaRESTService",
    "AlmaSRUService",
    #    "RepositoryService",
)
