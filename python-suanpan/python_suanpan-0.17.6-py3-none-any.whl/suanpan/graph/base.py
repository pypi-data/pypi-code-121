# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import api, error, g, objects


class Graph(object):
    def __init__(self, appId=g.appId):
        self.appId = appId
        self.graph = self.load(self.appId)

    def load(self, appId):
        return objects.Context(api.app.getAppGraph(appId))

    def reload(self):
        self.graph = self.load(self.appId)

    def update(self):
        api.app.updateAppGraph(self.appId, self.graph)

    def revert(self):
        api.app.revertAppGraph(self.appId)

    def getNodeById(self, nodeId):
        node = self.graph.processes[nodeId]
        if not node:
            raise error.GraphError(f"No such node {nodeId}")
        node.id = nodeId
        return node

    def getNodeByName(self, name):
        for nodeId, node in self.graph.processes.items():
            if node.metadata.label == name:
                node.id = nodeId
                return node
        raise error.GraphError(f"No such node {name}")

    def addConnection(self, sourceNodeId, sourcePortId, targetNodeId, targetPortId):
        self.graph.connections.append(
            {
                "src": {"process": sourceNodeId, "port": sourcePortId},
                "tgt": {"process": targetNodeId, "port": targetPortId},
            }
        )
        return self

    def modGlobalVar(self, globalVariables):
        for i, var in enumerate(globalVariables):
            self.graph.properties.globalVars[i].update(var)
        return self

    def modNodeParam(self, nodeId, params):
        getattr(self.graph.processes, nodeId).metadata["def"].params.update(params)
        return self
