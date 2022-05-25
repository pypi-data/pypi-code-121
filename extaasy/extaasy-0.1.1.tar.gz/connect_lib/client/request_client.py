#
# This file is part of the Ingram Micro CloudBlue Connect EaaS Extension Library.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#

"""
This module implements the Connect client methods for Request Flow
"""

from typing import List

from .. import consts
from connect.client import ClientError, R

from .client_manager import ClientManager
from ..request import Asset


class RequestClient(ClientManager):
    """
    Class to manage api request
    """

    def __init__(self, client):
        super().__init__(client)

    def approve_request(self, request_id: str, template_id: str) -> str:
        """
        Approve request

        :param request_id: request identifier
        :param template_id: template identifier

        :return: request status

        :raises: ClientError
        """

        try:
            request = self.client.requests[request_id](consts.APPROVE).post(
                payload={consts.TEMPLATE_ID: template_id})
            return request[consts.STATUS]
        except ClientError as ex:
            # Capturing Connect response "REQ_003 - Only pending and inquiring requests can be approved"
            if ex.error_code == consts.CONNECT_ERROR_CODE_APPROVE_NOT_PENDING_INQUIRING:
                return ""
            raise

    def fail_request(self, request_id: str, msg: str) -> str:
        """
        Fail request

        :param request_id: request identifier
        :param msg: message to be shown, human-readable

        :return: request status
        """

        request = self.client.requests[request_id](consts.FAIL).post(payload={consts.REASON: msg})
        return request[consts.STATUS]

    def update_request_asset_parameters(self, request_id: str, parameters: list) -> str:
        """
        Update request asset parameters

        :param request_id: request identifier
        :param parameters: parameters to be updated

        :return: request status
        """

        request = self.client.requests[request_id].update(payload={consts.ASSET: {consts.PARAMS: parameters}})
        return request[consts.STATUS]

    def get_other_assets(self, customer_id: str, product_id: str, asset_id: str, statuses: list) -> List[Asset]:
        """
        Returns a list of the customer's other assets for this product

        :param customer_id: customer identifier
        :param product_id: product identifier
        :param asset_id: asset identifier
        :param statuses: list ot expected status based on context

        :return: List of Asset
        """

        assets_data = self.client.assets.filter(
            R().tiers.customer.id.eq(customer_id) & R().product.id.eq(product_id) & R().id.ne(asset_id)
            & R().status.in_(statuses))

        if assets_data.first() is None:
            return []
        return [Asset(**a) for a in assets_data]

    def add_message(self, message: str, request_id: str) -> dict:
        """
        Add message to conversation

        :param message: message to be shown at Connect side
        :param request_id: request identifier

        :return: conversation
        """

        conversation = self.client.conversations.filter(instance_id=request_id).first()
        return self.client.conversations[conversation[consts.ID]](consts.MESSAGES).post(payload={consts.TEXT: message})
