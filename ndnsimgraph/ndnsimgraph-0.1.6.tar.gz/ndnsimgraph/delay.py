from enum import Enum
from typing import Optional
from .common import GraphBase, NodeItem
import numpy as np


class DelayType(Enum):
    """
    延迟类型
    https://ndnsim.net/current/metric.html
    """
    # LastDelay means that DelayS and DelayUS represent delay between last Interest sent and Data packet received
    # LastDelay意味着DelayS和DelayUS代表最后发送的兴趣和接收的数据包之间的延迟
    LastDelay = 0
    # FullDelay means that DelayS and DelayUS represent delay between first Interest sent and Data packet received
    # (i.e., includes time of Interest retransmissions)
    # FullDelay是指DelayS和DelayUS代表发送的第一个感兴趣的数据包和接收的数据包之间的延迟
    FullDelay = 1


class DelayTarget(Enum):
    """
    延迟目标
    """
    DelayS = 0  # 按秒统计的延迟
    DelayMS = 1  # 按毫秒统计的延迟
    DelayUS = 2  # 按微秒统计的延迟


class DelayItem:
    """
    一个用于描述 ndnsim 延迟采样结果的类
    https://ndnsim.net/current/metric.html#application-level-trace-helper
    """

    def __init__(self, Time: float, Node: str, AppId: int, SeqNo: int, Type: DelayType, DelayS: float,
                 DelayUS: float, RetxCount: int, HopCount: int):
        """
        :param Time:
        :param Node:
        :param AppId:
        :param SeqNo:
        :param Type:
        :param DelayS:
        :param DelayUS:
        :param RetxCount:
        :param HopCount:
        """
        self.Time = Time
        self.Node = Node
        self.AppId = AppId
        self.SeqNo = SeqNo
        self.Type = Type
        self.DelayS = DelayS
        self.DelayUS = DelayUS
        self.RetxCount = RetxCount
        self.HopCount = HopCount

    def getValueByDelayTarget(self, delayTarget: DelayTarget) -> float:
        if delayTarget == DelayTarget.DelayS:
            return self.DelayS
        elif delayTarget == DelayTarget.DelayMS:
            return self.DelayUS / 1000.0
        else:
            return self.DelayUS

    @staticmethod
    def parseLine(line: str):
        # 0.14809	C2	0	1	LastDelay	0.0610684	61068.4	1	3
        values = line.strip().split("\t")
        if len(values) < 9:
            return None
        return DelayItem(
            float(values[0].strip()),
            values[1].strip(),
            int(values[2].strip()),
            int(values[3].strip()),
            DelayType[values[4].strip()],
            float(values[5].strip()),
            float(values[6].strip()),
            int(values[7].strip()),
            int(values[8].strip())
        )


class NodeAppDelay:
    """
    用于描述某个节点上某个App的延迟 => 使用 AppId 来区分同一个节点上的不同App
    """

    def __init__(self, Node: str, AppId: int):
        self.Node = Node
        self.AppId = AppId
        self.typeMap = dict()  # 用于存储不同 Delay Type 的采样记录
        for delayType in DelayType:
            self.typeMap[delayType.name] = []

    def appendItem(self, item: DelayItem):
        """
        新增一条采样记录
        :param item:
        :return:
        """
        # 如果不是当前App的统计记录，忽略
        if item.Node != self.Node or item.AppId != self.AppId:
            return
        self.typeMap[item.Type.name].append(item)

    def getX(self, delayType: DelayType = DelayType.LastDelay, samplingInterval: float = 1.0):
        """
        获取采样时间列表
        :param delayType:
        :param samplingInterval:
        :return:
        """
        lastCount, res = 0, []
        for item in self.typeMap[delayType.name]:
            if int(item.Time / samplingInterval) != lastCount:
                lastCount = int(item.Time / samplingInterval)
            else:
                continue
            res.append(lastCount * samplingInterval)
        return res

    def getY(self, delayType: DelayType = DelayType.LastDelay,
             delayTarget: DelayTarget = DelayTarget.DelayMS,
             samplingInterval: float = 1.0):
        """
        获取延迟采样列表
        :param delayType:           延迟类型
        :param delayTarget:         延迟目标
        :param samplingInterval:    采样间隔
        :return:
        """
        lastCount, res, tmp = 0, [], []
        for item in self.typeMap[delayType.name]:
            if int(item.Time / samplingInterval) != lastCount:
                tmp.append(item.getValueByDelayTarget(delayTarget))
                lastCount = int(item.Time / samplingInterval)
            else:
                tmp.append(item.getValueByDelayTarget(delayTarget))
                continue
            res.append(np.average(tmp))
            tmp = []
        return res


class NodeDelay:
    """
    一个用于描述同一个节点上各个App延迟的类
    """

    def __init__(self, Node: str):
        self.Node = Node
        self.appMap = dict()

    def appendItem(self, item: DelayItem):
        """
        新增一条采样记录
        :param item:
        :return:
        """
        # 如果不是当前节点的采样记录，则忽略
        if item.Node != self.Node:
            return
        if item.AppId not in self.appMap:
            self.appMap[item.AppId] = NodeAppDelay(item.Node, item.AppId)
        self.appMap[item.AppId].appendItem(item)

    def getX(self, AppId: int, delayType: DelayType = DelayType.LastDelay, samplingInterval: float = 1.0):
        """
        获取某个App的采样时间列表
        :param AppId:
        :param delayType:
        :param samplingInterval:
        :return:
        """
        if AppId not in self.appMap:
            return []
        return self.appMap[AppId].getX(delayType, samplingInterval)

    def getY(self, AppId: int, delayType: DelayType = DelayType.LastDelay,
             delayTarget: DelayTarget = DelayTarget.DelayMS,
             samplingInterval: float = 1.0):
        """
        获取某个App的延迟采样列表
        :param AppId:
        :param delayType:
        :param delayTarget:
        :param samplingInterval:
        :return:
        """
        if AppId not in self.appMap:
            return []
        return self.appMap[AppId].getY(delayType, delayTarget, samplingInterval)


class Delay:
    """
    一个用于解析 ndnsim 延迟采样结果的类
    """

    def __init__(self):
        self.nodeMap = dict()

    def getByNode(self, node: str) -> Optional[NodeDelay]:
        if node not in self.nodeMap:
            return None
        return self.nodeMap[node]

    @staticmethod
    def parse(inputFile: str):
        """
        传入一个 ndnsim 采集的延迟采样结果文件，从中解析出延迟信息
        :param inputFile:
        :return:
        """
        delay = Delay()
        with open(inputFile, "r") as f:
            # 首先忽略表头
            # Time	Node	AppId	SeqNo	Type	DelayS	DelayUS	RetxCount	HopCount
            f.readline()

            # 从第一行开始解析
            line = f.readline()
            while line:
                if line.strip() != "":
                    item = DelayItem.parseLine(line)
                    if item:
                        if item.Node not in delay.nodeMap:
                            delay.nodeMap[item.Node] = NodeDelay(item.Node)
                        delay.nodeMap[item.Node].appendItem(item)
                line = f.readline()
        return delay


class DelayGraph(GraphBase):
    """
    一个用于实现绘制延迟图的类
    """

    def __init__(self, delay: Delay):
        super().__init__()
        self.delay = delay
        self.samplingInterval = 1.0
        self.delayType = DelayType.LastDelay
        self.delayTarget = DelayTarget.DelayMS

    def setSamplingInterval(self, samplingInterval: float):
        """
        设置采样间隔 => 如果 samplingInterval = 1.0 表示绘图时，每秒采样一次
        :param samplingInterval:
        :return:
        """
        self.samplingInterval = samplingInterval
        return self

    def setDelayType(self, delayType: DelayType):
        """
        设置延迟类型
        :param delayType:
        :return:
        """
        self.delayType = delayType
        return self

    def setDelayTarget(self, delayTarget: DelayTarget):
        """
        设置延迟目标
        :param delayTarget:
        :return:
        """
        self.delayTarget = delayTarget
        return self

    def plot(self, node: str, appId: int, *args,
             color: str = "&&",
             linewidth: float = 2, linestyle: str = "dotted", marker: str = "&&",
             markerfacecolor: str = "none", markersize: float = 6,
             **kwargs):
        node = self.delay.getByNode(node)
        if not node:
            print("not exist node: ", node)
            return self
        if "label" not in kwargs:
            kwargs["label"] = node.Node
        x, y = node.getX(appId, samplingInterval=self.samplingInterval), \
               node.getY(appId, self.delayType, self.delayTarget, self.samplingInterval)
        super().innerPlot(x, y, *args,
                          color=color,
                          linewidth=linewidth,
                          linestyle=linestyle,
                          marker=marker,
                          markerfacecolor=markerfacecolor,
                          markersize=markersize,
                          **kwargs)
        return self

    def plotSum(self, nodeList: [NodeItem], *args,
                color: str = "&&",
                linewidth: float = 2, linestyle: str = "dotted", marker: str = "&&",
                markerfacecolor: str = "none", markersize: float = 6,
                **kwargs):
        def getNode(nodeName):
            return self.delay.getByNode(nodeName)

        def getX(node: NodeDelay, nodeId):
            return node.getX(nodeId, samplingInterval=self.samplingInterval)

        def getY(node: NodeDelay, nodeId):
            return node.getY(nodeId, self.delayType, self.delayTarget, self.samplingInterval)

        super().innerPlotSum(nodeList, getNode, getX, getY, *args,
                             color=color,
                             linewidth=linewidth,
                             linestyle=linestyle,
                             marker=marker,
                             markerfacecolor=markerfacecolor,
                             markersize=markersize,
                             **kwargs)
        return self

    def plotAvg(self, nodeList: [NodeItem], *args,
                color: str = "&&",
                linewidth: float = 2, linestyle: str = "dotted", marker: str = "&&",
                markerfacecolor: str = "none", markersize: float = 6,
                **kwargs):

        def getNode(nodeName):
            return self.delay.getByNode(nodeName)

        def getX(node: NodeDelay, nodeId):
            return node.getX(nodeId, samplingInterval=self.samplingInterval)

        def getY(node: NodeDelay, nodeId):
            return node.getY(nodeId, self.delayType, self.delayTarget, self.samplingInterval)

        self.innerPlotAvg(nodeList, getNode, getX, getY, *args,
                          color=color,
                          linewidth=linewidth,
                          linestyle=linestyle,
                          marker=marker,
                          markerfacecolor=markerfacecolor,
                          markersize=markersize,
                          **kwargs)
        return self

    @staticmethod
    def parse(inputFile: str):
        return DelayGraph(Delay.parse(inputFile))
