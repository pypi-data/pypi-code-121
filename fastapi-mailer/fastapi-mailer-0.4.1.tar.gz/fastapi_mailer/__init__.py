from fastapi_mailer.config import ConnectionConfig
from fastapi_mailer.fastmail import FastMail
from fastapi_mailer.schemas import MessageSchema, MultipartSubtypeEnum

from . import email_utils

__version__ = '0.4.1'


__author__ = 'sabuhi.shukurov@gmail.com'


__all__ = ['FastMail', 'ConnectionConfig', 'MessageSchema', 'email_utils', 'MultipartSubtypeEnum']
