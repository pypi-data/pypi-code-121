# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.utils.assess.duck_utils import len_or_zero


class Preshift(object):
    """
    Holder class for information prior to shifting
    """

    def __init__(self, self_obj, call_args, call_kwargs):
        self.obj = self_obj
        self.obj_length = len_or_zero(self_obj)
        self.args = call_args or []
        self.kwargs = call_kwargs or {}

    def __repr__(self):
        return f"<Preshift({self.obj}, {self.args}, {self.kwargs})>"
