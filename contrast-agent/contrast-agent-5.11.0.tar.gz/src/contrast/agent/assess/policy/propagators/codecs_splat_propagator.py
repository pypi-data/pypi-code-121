# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from .splat_propagator import SplatPropagator


class CodecsSplatPropagator(SplatPropagator):
    def __init__(self, *args, **kwargs):
        """
        Most codecs methods return a tuple where the target string is the first element
        """
        super().__init__(*args, **kwargs)
        self.target = self.target[0]
