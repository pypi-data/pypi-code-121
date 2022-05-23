#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author : SandQuant
# @Email: data@sandquant.com

from .client import SandInvestClient
from .api import *
from .utils import *
from .fields import *

from .__version__ import __title__, __description__, __copyright__
from .__version__ import __version__, __author__, __author_email__

auto_login = SandInvestClient.auto_login
unregister = SandInvestClient.unregister
settings = SandInvestClient.settings


def login(account, password):
    return SandInvestClient.login(**locals())


def register(account, password):
    return SandInvestClient.register(**locals())


auto_login()
