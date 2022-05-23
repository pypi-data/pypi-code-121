# Copyright (C) 2016 Ipsilon project Contributors, for license see COPYING

import base64
from cryptography.hazmat.primitives.constant_time import bytes_eq
import os
from six import binary_type


def generate_random_secure_string(size=32):
    return base64.urlsafe_b64encode(os.urandom(size))[:size].decode('utf-8')


def constant_time_string_comparison(stra, strb):
    if not isinstance(stra, binary_type):
        stra = stra.encode('utf-8')
    if not isinstance(strb, binary_type):
        strb = strb.encode('utf-8')
    return bytes_eq(stra, strb)
