# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import base64

from contrast.utils.string_utils import ensure_string


def base64_encode(to_encode):
    """
    Allows you to encode string to Base64
    """
    if isinstance(to_encode, str):
        input_object = to_encode.encode("utf-8")
    else:
        input_object = to_encode

    output_object = base64.b64encode(input_object)

    return output_object.decode("ascii")


def base64_decode(to_decode):
    """
    Allows you to decode Base64 to str
    """
    output_object = base64.urlsafe_b64decode(ensure_string(to_decode))
    return ensure_string(output_object)
