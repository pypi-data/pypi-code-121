# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Services exceptions."""


class AlmaAPIError(Exception):
    """Alma API error class."""


class AlmaRESTError(Exception):
    """Alma Rest API error class."""

    def __init__(self, code, msg):
        """Constructor for alma rest error."""
        super().__init__(f"Alma API error code={code} msg='{msg}'")


class AlmaSRUError(Exception):
    """Alma SRU error class."""

    def __init__(self, code, msg):
        """Constructor for alma sru error."""
        super().__init__(f"Alma sru error code={code} msg='{msg}'")
