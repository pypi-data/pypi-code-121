import sys
import os

from requests.exceptions import RequestException
import requests as request

sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..", "..", "..")))
from netskope.api.iterator.operation import Operation
from requests.auth import AuthBase
from netskope.api.iterator.const import Const



import logging
import re

from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger()


class AuthToken(AuthBase):
    """Netskope-API-Token Auth for header token."""

    def __init__(self, token):
        """Initialize the object."""
        self.token = token

    def __call__(self, req):
        """Set Netskope-Api-Token in request"""
        req.headers["Netskope-Api-Token"] = "{}".format(self.token)
        return req


class NetskopeIteratorClient:
    """Iterator client for netskope event downloads"""

    def __init__(self,params):
        """

        :param params:
        """

        configs = {
            "base_url": "https://{}".format(params.get(Const.NSKP_TENANT_HOSTNAME)),
            "iterator_name": params.get(Const.NSKP_ITERATOR_NAME),
            "eventtype" : params.get(Const.NSKP_EVENT_TYPE)
        }
        self.token = params.get(Const.NSKP_TOKEN)

        headers = {
            "User-Agent": "DataExport-Iterator-{}".format( params.get("HOSTNAME")),
        }

        self.configs = configs
        self.session = request.Session()
        self.session.headers.update(headers)
        self.session.auth = AuthToken(self.token)
        self.session.hooks['response'].append(self.response_hook)

    def response_hook(self, res, *args, **kwargs):
        """
        :param res:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            data = res.json()
        except Exception:
            if "429 Too Many Requests" in res.text:
                raise RequestException(res.text)
            return res

        #TODO Based on the response value the client side sleep will be introduced.

        return res

    # Construct the url as per the operation.
    def build_url(self, op):
        """

        :param op : Operation to be invoked:
        :return The Iterator API to be called:
        """
        base_url = self.configs.get("base_url")
        event_type = self.configs.get("eventtype")
        tenant = self.configs.get("tenant")
        iterator_name = self.configs.get("iterator_name")
        url = "{}/api/v2/events/dataexport/events/{}?index={}&operation={}".format(base_url,event_type,iterator_name,op)
        return url


    # Download the response based on the operation.
    def get(self, operation):
        """
        :param operation: Operation to be invoked
        :return Response objects for the operation.
        """

        op = self.validate_and_return_operation(operation)
        url = self.build_url(op)
        #TOD0 : Verify has to be set to True for the production tenants.
        res = self.session.get(url)
        return res

    def validate_and_return_operation(self, op):
        """Raise an exception if the iterator operation is not valid.
        The operation can be: next, head, tail, resend, or a timestamp value.
        """
        if op in (Operation.OP_HEAD, Operation.OP_TAIL, Operation.OP_NEXT, Operation.OP_RESEND):
            return op.value

        try:
            return int(op)
        except Exception as e:
            raise ValueError("Invalid iterator operation: {}".format(op))

        if ts < 0:
            raise ValueError("Invalid iterator operation as timestamp: {}".format(op))

