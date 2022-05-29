from enum import Enum
from typing import Optional
from .common import GraphBase, NodeItem


class DropType(Enum):
    """
    丢包类型
    https://ndnsim.net/current/metric.html
    """
    Drop = 0


class DropTarget(Enum):
    """
    丢包目标
    https://ndnsim.net/current/metric.html
    """
    Packets = 0  # estimated rate (EWMA average) of packets within the last averaging period (number of packets/s)
    Kilobytes = 1  # estimated rate (EWMA average) within last averaging period (kilobytes/s)
    PacketRaw = 2  # absolute number of packets within last averaging period (number of packets).
    KilobytesRaw = 3  # absolute number of kilobytes transferred within the last averaging period (number of packets).


class DropItem:
    """
    一个用于描述 ndnsim 丢包采样结果的类
    """

    def __init__(self, Time: float, Node: str, Interface: str, Type: DropType, Packets: float,
                 Kilobytes: float, PacketsRaw: float, KilobytesRaw: float):
        self.Time = Time
        self.Node = Node
        self.Interface = Interface
        self.Type = Type
        self.Packets = Packets
        self.Kilobytes = Kilobytes
        self.PacketsRaw = PacketsRaw
        self.KilobytesRaw = KilobytesRaw

    def getValueByDropTarget(self, dropTarget: DropTarget):
        if dropTarget == DropTarget.Packets:
            return self.Packets
        elif dropTarget == DropTarget.Kilobytes:
            return self.Kilobytes
        elif dropTarget == DropTarget.PacketRaw:
            return self.PacketsRaw
        else:
            return self.KilobytesRaw

    @staticmethod
    def parseLine(line: str):
        # 0.5	C1	combined	Drop	0	0	0	0
        values = line.strip().split("\t")
        if len(values) < 8:
            return None
        return DropItem(
            float(values[0].strip()),
            values[1].strip(),
            values[2].strip(),
            DropType[values[3].strip()],
            float(values[4].strip()),
            float(values[5].strip()),
            float(values[6].strip()),
            float(values[7].strip()),
        )


class NodeFaceDrop:
    """
    一个用于描述某个接口丢包情况的类
    """

    def __init__(self, Node: str, Interface: str):
        self.Node = Node
        self.Interface = Interface
        self.typeMap = dict()  # 用于存储不同 Drop Type 的采样记录
        for dropType in DropType:
            self.typeMap[dropType.name] = []

    def appendItem(self, item: DropItem):
        """
        新增一条采样记录
        :param item:
        :return:
        """
        # 如果不是当前接口的统计记录，忽略
        if item.Node != self.Node or item.Interface != self.Interface:
            return
        self.typeMap[item.Type.name].append(item)

    def getX(self, dropType: DropType = DropType.Drop, samplingInterval: float = 1.0):
        """
        获取采样时间列表
        :param dropType:
        :param samplingInterval:
        :return:
        """
        lastCount, res = 0, []
        for item in self.typeMap[dropType.name]:
            if int(item.Time / samplingInterval) != lastCount:
                lastCount = int(item.Time / samplingInterval)
            else:
                continue
            res.append(lastCount * samplingInterval)
        return res

    def getY(self, dropType: DropType = DropType.Drop,
             dropTarget: DropTarget = DropTarget.PacketRaw,
             samplingInterval: float = 1.0):
        """
        获取丢包数统计列表
        :param dropType:
        :param dropTarget:
        :param samplingInterval:
        :return:
        """
        lastCount, res, currentDropPacketsNum = 0, [], 0
        for item in self.typeMap[dropType.name]:
            if int(item.Time / samplingInterval) != lastCount:
                lastCount = int(item.Time / samplingInterval)
                currentDropPacketsNum += item.getValueByDropTarget(dropTarget)
                res.append(currentDropPacketsNum)
                currentDropPacketsNum = 0
            else:
                currentDropPacketsNum += item.getValueByDropTarget(dropTarget)
                continue
        return res


class NodeDrop:
    """
    一个用于描述节点各个接口丢包的类
    """

    def __init__(self, Node: str):
        self.interfaceMap = dict()
        self.Node = Node

    def appendItem(self, item: DropItem):
        """
        新增一条采样记录
        :param item:
        :return:
        """
        # 如果不是当前节点的统计记录，忽略
        if item.Node != self.Node:
            return
        if item.Interface not in self.interfaceMap:
            self.interfaceMap[item.Interface] = NodeFaceDrop(item.Node, item.Interface)
        self.interfaceMap[item.Interface].appendItem(item)

    def getX(self, interface: str = "combined", dropType: DropType = DropType.Drop,
             samplingInterval: float = 1.0) -> [float]:
        """
        获取采样时间列表
        :param interface:
        :param dropType:
        :param samplingInterval:
        :return:
        """
        if interface not in self.interfaceMap:
            return []
        return self.interfaceMap[interface].getX(dropType, samplingInterval)

    def getY(self, interface: str, dropType: DropType = DropType.Drop, dropTarget: DropTarget = DropTarget.PacketRaw,
             samplingInterval: float = 1.0) -> [float]:
        """
        获取丢包数统计列表
        :param interface:
        :param dropType:
        :param dropTarget:
        :param samplingInterval:
        :return:
        """
        if interface not in self.interfaceMap:
            return []
        return self.interfaceMap[interface].getY(dropType, dropTarget, samplingInterval)


class Drop:
    """
    一个用于解析 ndnsim 丢包统计结果的类
    """

    def __init__(self):
        self.nodeMap = dict()

    def getByNode(self, node: str) -> Optional[NodeDrop]:
        if node not in self.nodeMap:
            return None
        return self.nodeMap[node]

    @staticmethod
    def parse(inputFile: str):
        """
        传入一个 ndnsim 丢包统计结果文件，从中解析出丢包数据
        :param inputFile:
        :return:
        """
        drop = Drop()
        with open(inputFile, "r") as f:
            # 首先忽略表头
            # Time	Node	Interface	Type	Packets	Kilobytes	PacketsRaw	KilobytesRaw
            f.readline()

            # 从第一行开始解析
            line = f.readline()
            while line:
                if line.strip() != "":
                    item = DropItem.parseLine(line)
                    if item:
                        if item.Node not in drop.nodeMap:
                            drop.nodeMap[item.Node] = NodeDrop(item.Node)
                        drop.nodeMap[item.Node].appendItem(item)
                line = f.readline()
        return drop


class DropGraph(GraphBase):
    """
    一个用于实现绘制丢包数图的类
    """

    def __init__(self, drop: Drop):
        super().__init__()
        self.drop = drop
        self.samplingInterval = 1.0
        self.dropType = DropType.Drop
        self.dropTarget = DropTarget.PacketRaw

    def setSamplingInterval(self, samplingInterval: float):
        """
        设置采样间隔 => 如果 samplingInterval = 1.0 表示绘图时，每秒采样一次
        :param samplingInterval:
        :return:
        """
        self.samplingInterval = samplingInterval
        return self

    def setDropType(self, dropType: DropType):
        """
        设置丢包类型
        :param dropType:
        :return:
        """
        self.dropType = dropType
        return self

    def setDropTarget(self, dropTarget: DropTarget):
        """
        设置丢包目标
        :param dropTarget:
        :return:
        """
        self.dropTarget = dropTarget
        return self

    def plot(self, node: str, *args,
             interface: str = "combined",
             color: str = "&&",
             linewidth: float = 2, linestyle: str = "dotted", marker: str = "&&",
             markerfacecolor: str = "none", markersize: float = 6,
             **kwargs):
        node = self.drop.getByNode(node)
        if not node:
            print("not exist node: ", node)
            return self
        if "label" not in kwargs:
            kwargs["label"] = node.Node
        x, y = node.getX(interface, samplingInterval=self.samplingInterval), \
               node.getY(interface, self.dropType, self.dropTarget, self.samplingInterval)
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
            return self.drop.getByNode(nodeName)

        def getX(node: NodeDrop, nodeId):
            return node.getX(nodeId, samplingInterval=self.samplingInterval)

        def getY(node: NodeDrop, nodeId):
            return node.getY(nodeId, self.dropType, self.dropTarget, self.samplingInterval)

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
            return self.drop.getByNode(nodeName)

        def getX(node: NodeDrop, nodeId):
            return node.getX(nodeId, samplingInterval=self.samplingInterval)

        def getY(node: NodeDrop, nodeId):
            return node.getY(nodeId, self.dropType, self.dropTarget, self.samplingInterval)

        self.innerPlotAvg(nodeList, getNode, getX, getY, *args,
                          color=color,
                          linewidth=linewidth,
                          linestyle=linestyle,
                          marker=marker,
                          markerfacecolor=markerfacecolor,
                          markersize=markersize,
                          **kwargs)
        return self

    def innerParse(self, inputFile: str):
        self.drop = Drop.parse(inputFile)
        return self

    @staticmethod
    def parse(inputFile: str):
        return DropGraph(Drop.parse(inputFile))
