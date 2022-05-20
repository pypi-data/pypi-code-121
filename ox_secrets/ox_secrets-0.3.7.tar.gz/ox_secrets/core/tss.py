"""Telegram secret server.

This module provides a secret server using the telegram API.
This is helpful for local testing and very simple operation.
"""

import typing
import logging
import csv
import os

from ox_secrets import settings
from ox_secrets.core import common


class TelegramSecretServer(common.SecretServer):
    """Class to handle getting secrets from telegram.
    """

    @classmethod
    def one_time_secret(cls, tuser, name, category='root'):
        FIXME
        
            
    @classmethod
    @classmethod
    def load_cache(cls, name: typing.Optional[str] = None,
                   category: typing.Optional[str] = None):
        "Implement loading cache from a file."
        return cls.load_secrets_file()
