# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import g


class Interface(object):
    def __init__(self, request):
        super().__init__()
        self.request = request

    def init(self, suanpanUrl, userId=None, accessKey=None, accessSecret=None):
        return self.request.post(
            "/api/suanpan/init",
            json={
                "suanpanUrl": suanpanUrl,
                "userId": userId or g.userId,
                "accessKey": accessKey or g.accessKey,
                "accessSecret": accessSecret or g.accessSecret,
            },
        )
