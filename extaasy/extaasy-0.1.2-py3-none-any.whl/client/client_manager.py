#
# This file is part of the Ingram Micro CloudBlue Connect EaaS Extension Library.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#

"""
This module implements the Connect client common methods for all flows
"""

from ..request import Asset


class ClientManager:
    """
    Class to manage api common needs
    """

    def __init__(self, client):
        self.client = client

    def get_asset(self, asset_id: str) -> Asset:
        """
        Obtain asset from Connect by its identifier, and then deserialize it.

        :param asset_id: asset identifier

        :return: Asset
        """

        return Asset(**self.client.assets[asset_id].get())
