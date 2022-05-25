# -*- coding: utf-8 -*-
"""
@File        : error_response.py
@Author      : yu wen yang
@Time        : 2022/5/12 1:24 下午
@Description :
"""
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder

from departments.common.config import BadRequestCode, Ok


class BadBaseResponse(JsonResponse):
    status_code = BadRequestCode
    default_detail = "bad request"
    default_code = "error"

    def __init__(
            self,
            detail=None,
            code=None,
            encoder=DjangoJSONEncoder,
            safe=True,
            json_dumps_params=None,
            **kwargs,
    ):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        super().__init__({'detail': detail, 'code': code}, encoder, safe, json_dumps_params, **kwargs)


class FailedValue(BadBaseResponse):
    status_code = BadRequestCode
    default_detail = "failed value"
    default_code = "failed"


class Resp(dict):
    default_code = Ok
    default_msg = "success"

    def __init__(self, code=None, msg=None, data={}, **kwargs):

        if code is None:
            code = self.default_code
        if msg is None:
            msg = self.default_msg

        dic = {"code": code, "msg": msg, "data": {}}

        dic["data"] = data
        dic.update(kwargs)
        super().__init__(dic, **kwargs)



