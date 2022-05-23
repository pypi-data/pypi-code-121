# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import g
from suanpan.api.requests import affinity


def listComponents(limit=9999):
    return affinity.post("/component/list", json={"limit": limit})["list"]


def getComponentGraph(componentId):
    return affinity.get(f"/component/graph/{componentId}")["data"]


def updateComponentGraph(componentId, graph):
    return affinity.post(f"/component/graph/{componentId}", json={"graph": graph})


def revertComponentGraph(componentId):
    return affinity.post(f"/component/graph/{componentId}/revert")


def shareComponent(componentId, userId, name):
    return affinity.post(
        "/component/share",
        json={"id": componentId, "targetUserId": userId, "name": name},
    )


def exportModel(portId, name, appId=None, nodeId=None, overwrite=False):
    return affinity.post(
        "/component/export/model",
        json={
            "id": appId or g.appId,
            "nodeId": nodeId or g.nodeId,
            "portId": portId,
            "name": name,
            "overwrite": overwrite,
        },
    )
