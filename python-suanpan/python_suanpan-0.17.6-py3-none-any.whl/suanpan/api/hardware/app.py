# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.api import app
from suanpan.utils import json


class Interface(object):
    def __init__(self, request):
        super().__init__()
        self.request = request

    def create(self, appId):
        return self.request.post(
            "/api/app", json={"id": appId, "graph": json.dumps(app.getAppGraph(appId))}
        )

    def delete(self, appId):
        return self.request.delete(f"/api/app/{appId}")
