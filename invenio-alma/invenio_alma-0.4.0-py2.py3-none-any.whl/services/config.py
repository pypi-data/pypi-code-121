# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Alma Service config class."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AlmaRESTConfig:
    """Alma service configuration class."""

    api_key: str = ""
    api_host: str = ""


@dataclass(frozen=True)
class AlmaSRUConfig:
    """Alma sru service config."""

    search_key: str = ""
    domain: str = ""
    institution_code: str = ""
