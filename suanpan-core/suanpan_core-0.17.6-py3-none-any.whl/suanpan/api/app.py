# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import g
from suanpan.api.requests import affinity


def getAppGraph(appId):
    return affinity.get(f"/app/graph/{appId}")["data"]


def updateAppGraph(appId, graph):
    return affinity.post(f"/app/graph/{appId}", json={"graph": graph})


def revertAppGraph(appId):
    return affinity.post(f"/app/graph/{appId}/revert")


def checkAppStatus(appId=None):
    return affinity.post("/app/status", json={"id": appId or g.appId})


# mode: runStart, runStop, runStartStop
def runApp(nodeId, appId=None, mode="runStart"):
    return affinity.post(
        "/app/run", json={"id": appId or g.appId, "nodeId": nodeId, "type": mode}
    )


def startAppCron(
    period, mode, startEffectTime, endEffectTime, nodeId, config, appId=None
):
    return affinity.post(
        "/app/cron/start",
        json={
            "id": appId or g.appId,
            "cronConfig": {
                "period": period,
                "runType": mode,
                "startEffectTime": startEffectTime,
                "endEffectTime": endEffectTime,
                "nodeId": nodeId,
                "config": config,
            },
        },
    )


def stopAppCron(appId=None):
    return affinity.post("/app/cron/stop", json={"id": appId or g.appId})


def createApp(appName, appType, dirId=None):
    return affinity.post(
        "/app/create", json={"name": appName, "dir": dirId, "type": appType}
    )


def deleteApp(appId=None):
    return affinity.post("/app/del", json={"id": appId or g.appId})


def copyApp(name, appType, appId=None, withData=False, description=None, dirId=None):
    return affinity.post(
        "/app/duplicate",
        json={
            "id": appId or g.appId,
            "name": name,
            "dir": dirId,
            "type": appType,
            "withData": withData,
            "description": description,
        },
    )


def listApp(appType, withStatus=False, limit=9999):
    return affinity.post(
        "/app/list", json={"limit": limit, "type": appType, "withStatus": withStatus}
    )
