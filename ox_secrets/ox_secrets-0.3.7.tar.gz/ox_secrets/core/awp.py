"""AWS Parameter Store

This module provides a "secret" server using the AWS parameter store.
Generally these will not be secret unless you manage encryption/decryption
yourself (or with ox_secrets).

The main advantage of the AWS parameter store is that it is free for
the String type. One downside is that it has a maximum of 10,000 values.
"""


import logging
import csv
import os
import typing
import json


try:
    import boto3
except Exception as problem:
    logging.warning(
        'Unable to import boto3 because %s; aws parameters unavailable',
        str(problem))


from ox_secrets import settings
from ox_secrets.core import common


class AWSParameterServer(common.SecretServer):
    """Class to handle parameters from AWS.
    """

    @classmethod
    def load_parameter_from_aws(
            cls, parameter_id: str, profile_name: typing.Optional[
                str] = None) -> typing.Dict[str, str]:
        if profile_name is None:
            profile_name = settings.OX_SECRETS_AWS_PROFILE_NAME
        logging.warning(
            'Connecting to boto3 for profile %s to read parameters for %s',
            profile_name, parameter_id)
        session = boto3.Session(profile_name=profile_name)
        FIXME
        return secret_dict
        
    @classmethod
    def load_cache(cls, name: typing.Optional[str] = None,
                   category: typing.Optional[str] = None,
                   loader_params: typing.Optional[dict] = None):
        """Load parameters and cache them from back-end store.

        :param name:  String name of parameter desired. If this is None, then
                      all parameters for given category are loaded.

        :param category:  String name of parameter desired. Same as parameter-id for
                          AWS command line interface.


        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  Fill cls._cache with data from parameters store.
                  Sub-classes must implement.

        """
        loader_params = loader_params if loader_params is not None else {}
        data = cls.load_parameter_from_aws(parameter_id=category, **loader_params)
        assert isinstance(data, dict)
        with cls._lock:
            cdict = cls._cache.get(category, {})
            if not cdict:
                cls._cache[category] = cdict
            cdict.update(data)

        
