# coding=utf-8
from __future__ import absolute_import, print_function

import base64
import hashlib
import hmac

from suanpan import error, g, utils


def signatureV1(secret, data):
    h = hmac.new(utils.encode(secret), utils.encode(data), hashlib.sha1)
    return utils.decode(base64.b64encode(utils.encode(h.digest())))


def defaultHeaders():
    if not g.userIdHeaderField:
        raise error.ApiError("UserIdHeaderField not set")
    return {
        g.userIdHeaderField: g.userId,
        g.userSignatureHeaderField: signatureV1(g.accessSecret, g.userId),
        g.userSignVersionHeaderField: "v1",
    }
