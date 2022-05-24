#!/usr/bin/env python3
# coding: utf-8

import flask
# noinspection PyPackageRequirements
import werkzeug.exceptions
from joker.redis.error import ErrorInterface
from volkanic import errors

from joker.flasky import viewutils
from joker.flasky.viewutils import decorate_all_view_funcs


class Application(flask.Flask):
    json_encoder = viewutils.JSONEncoderPlus
    decorate_all_view_funcs = decorate_all_view_funcs
    serialize_current_session = viewutils.serialize_current_session

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_interface = None

    def use_default_error_handlers(self, error_interface: ErrorInterface):
        if self.error_interface is not None:
            return
        self.error_interface = error_interface

        @self.errorhandler(errors.KnownError)
        def on_known_error(error: errors.KnownError):
            return error.to_dict()

        @self.errorhandler(Exception)
        def on_error(error: Exception):
            # https://flask.palletsprojects.com/en/2.0.x/errorhandling/#generic-exception-handlers
            if isinstance(error, werkzeug.exceptions.HTTPException):
                return error
            errinfo = error_interface.dump()
            return errinfo.to_dict()


__all__ = ['Application']
