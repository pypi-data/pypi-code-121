# -*- coding:utf-8 -*-
'''
Basic root blueprint entry point.
'''
import os
import flask
from . import conf
from . import event
from .exceptions import PbException


pb_root = flask.Blueprint("pb_root", __name__,
                          template_folder=os.path.abspath(os.path.dirname(__file__) + '/../templates'))

__ALL__ = ['pb_root', 'conf', 'event', 'PbException']
