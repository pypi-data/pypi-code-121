from enum import Enum
from typing import Optional
from .common import GraphBase, NodeItem
import numpy as np
import pandas as pd


class ThroughputType(Enum):
    """
    吞吐量类型
    https://ndnsim.net/current/metric.html
    """
    InInterests = 0
    OutInterests = 1
    InData = 2
    OutData = 3
    InNacks = 4
    OutNacks = 5
    InSatisfiedInterests = 6
    InTimedOutInterests = 7
    OutSatisfiedInterests = 8
    OutTimedOutInterests = 9

    # 下面的类型只在 FaceId = -1 有效
    SatisfiedInterests = 10
    TimedOutInterests = 11


class ThroughputTarget(Enum):
    """
    吞吐量目标
    https://ndnsim.net/current/metric.html
    """
    # estimated rate (EWMA average) of packets within the last averaging period (number of packets/s)
    Packets = 0

    # estimated rate (EWMA average) within last averaging period (kilobytes/s)
    Kilobytes_KBps = 1
    Kilobytes_MBps = 2
    Kilobytes_Kbps = 3
    Kilobytes_Mbps = 4

    # absolute number of packets within last averaging period (number of packets).
    PacketRaw = 5

    # absolute number of kilobytes transferred within the last averaging period (number of packets).
    KilobytesRaw_KBps = 6
    KilobytesRaw_MBps = 7
    KilobytesRaw_Kbps = 8
    KilobytesRaw_Mbps = 9

    @staticmethod
    def getUnit(throughputTargetName: str) -> str:
        value = ThroughputTarget[throughputTargetName].value
        if value == 0 or value == 5:
            return "Number of packets"
        elif value == 1 or value == 6:
            return "KBps"
        elif value == 2 or value == 7:
            return "MBps"
        elif value == 3 or value == 8:
            return "Kbps"
        elif value == 4 or value == 9:
            return "Mbps"
        else:
            return "unknown"


class ThroughputItem:
    """
    一个用于描述 ndnsim 吞吐量采样结果的类
    """

    def __init__(self, Time: float, Node: str, FaceId: int, FaceDescr: str, Type: ThroughputType,
                 Packets: float, Kilobytes: float, PacketRaw: float, KilobytesRaw: float):
        """
        :param Time:        时间，例如: 0.5
        :param Node:        节点名称，例如：C1
        :param FaceId:      Face id
        :param FaceDescr:   Face 描述
        :param Type:
        :param Packets:
        :param Kilobytes:
        :param PacketRaw:
        :param KilobytesRaw:
        """
        self.Time = Time  # simulation time
        self.Node = Node  # node id, globally unique
        self.FaceId = FaceId  # interface ID (-1 for combined metric)
        self.FaceDescr = FaceDescr
        self.Type = Type
        self.Packets = Packets
        self.Kilobytes = Kilobytes
        self.PacketRaw = PacketRaw
        self.KilobytesRaw = KilobytesRaw

    def getValueByThroughputTarget(self, throughputTarget: ThroughputTarget, lpPacketHeaderSize: int = 0):
        kilobytes, kilobytesRaw = self.Kilobytes, self.KilobytesRaw
        if kilobytes > 0:
            kilobytes += ((self.Packets * lpPacketHeaderSize) / 1000)
        if kilobytesRaw > 0:
            kilobytesRaw += ((self.PacketRaw * lpPacketHeaderSize) / 1000)
        if throughputTarget == ThroughputTarget.Packets:
            return self.Packets
        elif throughputTarget == ThroughputTarget.Kilobytes_KBps:
            return kilobytes
        elif throughputTarget == ThroughputTarget.Kilobytes_MBps:
            return kilobytes / 1000
        elif throughputTarget == ThroughputTarget.Kilobytes_Kbps:
            return kilobytes * 8
        elif throughputTarget == ThroughputTarget.Kilobytes_Mbps:
            return kilobytes * 8 / 1000
        elif throughputTarget == ThroughputTarget.PacketRaw:
            return self.PacketRaw
        elif throughputTarget == ThroughputTarget.KilobytesRaw_KBps:
            return kilobytesRaw
        elif throughputTarget == ThroughputTarget.KilobytesRaw_MBps:
            return kilobytesRaw / 1000
        elif throughputTarget == ThroughputTarget.KilobytesRaw_Kbps:
            return kilobytesRaw * 8
        elif throughputTarget == ThroughputTarget.KilobytesRaw_Mbps:
            return kilobytesRaw * 8 / 1000

    @staticmethod
    def parseLine(line: str):
        # 0.5	C1	1	internal://	InInterests	0	0	0	0
        values = line.strip().split("\t")
        if len(values) != 9:
            return None
        return ThroughputItem(float(values[0].strip()),
                              values[1].strip(),
                              int(values[2].strip()),
                              values[3].strip(),
                              ThroughputType[values[4].strip()],
                              float(values[5].strip()),
                              float(values[6].strip()),
                              float(values[7].strip()),
                              float(values[8].strip()),
                              )


class NodeFaceThroughput:
    """
    一个用于描述节点某个接口吞吐量的类
    """

    def __init__(self, Node: str, FaceId: int):
        self.Node = Node
        self.FaceId = FaceId
        self.typeMap = dict()  # 用于存储不同 Throughput Type 的采样记录
        for throughputType in ThroughputType:
            self.typeMap[throughputType.name] = []

    def appendItem(self, item: ThroughputItem):
        """
        新增一条采样记录
        :param item:
        :return:
        """
        # 如果不是当前接口的统计记录，忽略
        if item.Node != self.Node or item.FaceId != self.FaceId:
            return
        self.typeMap[item.Type.name].append(item)

    def getX(self, throughputType: ThroughputType = ThroughputType.OutData, samplingInterval: float = 1.0):
        """
        获取采样时间列表
        :param throughputType:
        :param samplingInterval:
        :return:
        """
        lastCount, res = 0, []
        if len(self.typeMap[throughputType.name]) <= 0:
            return []
        item = self.typeMap[throughputType.name][0]
        if item.Time / samplingInterval > 0:
            for i in range(int(item.Time / samplingInterval)):
                res.append((i + 1) * samplingInterval)
                lastCount = i + 1
        for item in self.typeMap[throughputType.name]:
            if int(item.Time / samplingInterval) != lastCount:
                lastCount = int(item.Time / samplingInterval)
            else:
                continue
            res.append(lastCount * samplingInterval)
        return res

    def getY(self, throughputType: ThroughputType = ThroughputType.OutData,
             throughputTarget: ThroughputTarget = ThroughputTarget.Kilobytes_KBps,
             samplingInterval: float = 1.0, lpPacketHeaderSize: int = 0):
        """
        获取吞吐量列表
        :param lpPacketHeaderSize:      LpPacket Header 大小
        :param throughputType:          吞吐量类型
        :param throughputTarget:        吞吐量目标
        :param samplingInterval:       采样间隔
        :return:
        """
        lastCount, res = 0, []
        if len(self.typeMap[throughputType.name]) <= 0:
            return []
        item = self.typeMap[throughputType.name][0]
        if item.Time / samplingInterval > 0:
            for i in range(int(item.Time / samplingInterval)):
                res.append(0)
                lastCount = i + 1
        for item in self.typeMap[throughputType.name]:
            if int(item.Time / samplingInterval) != lastCount:
                lastCount = int(item.Time / samplingInterval)
            else:
                continue
            res.append(item.getValueByThroughputTarget(throughputTarget, lpPacketHeaderSize))
        return res


class NodeThroughput:
    """
    一个用于描述节点各个接口吞吐量的类
    """

    def __init__(self, Node: str):
        self.faceIdMap = dict()
        self.Node = Node

    def appendItem(self, item: ThroughputItem):
        """
        新增一条采样记录
        :param item:
        :return:
        """
        # 如果不是当前节点的统计记录，忽略
        if item.Node != self.Node:
            return
        if item.FaceId not in self.faceIdMap:
            self.faceIdMap[item.FaceId] = NodeFaceThroughput(item.Node, item.FaceId)
        self.faceIdMap[item.FaceId].appendItem(item)

    def getX(self, FaceId: int, throughputType: ThroughputType = ThroughputType.OutData,
             samplingInterval: float = 1.0) -> [float]:
        """
        获取采样时间列表
        :param FaceId:
        :param throughputType:
        :param samplingInterval:
        :return:
        """
        if FaceId not in self.faceIdMap:
            return []
        return self.faceIdMap[FaceId].getX(throughputType, samplingInterval)

    def getY(self, FaceId: int, throughputType: ThroughputType = ThroughputType.OutData,
             throughputTarget: ThroughputTarget = ThroughputTarget.Kilobytes_KBps, samplingInterval: float = 1.0,
             lpPacketHeaderSize: int = 0):
        """
        获取吞吐量列表
        :param lpPacketHeaderSize:      LpPacket Header 大小
        :param FaceId:                  FaceId
        :param throughputType:          吞吐量类型
        :param throughputTarget:        吞吐量目标
        :param samplingInterval:       采样间隔
        :return:
        """
        if FaceId not in self.faceIdMap:
            return []
        return self.faceIdMap[FaceId].getY(throughputType, throughputTarget, samplingInterval, lpPacketHeaderSize)


class Throughput:
    """
    一个用于解析 ndnsim 吞吐量采样结果的类
    """

    def __init__(self):
        self.nodeMap = dict()

    def getByNode(self, node: str) -> Optional[NodeThroughput]:
        if node not in self.nodeMap:
            return None
        return self.nodeMap[node]

    @staticmethod
    def parse(inputFile: str):
        """
        传入一个 ndnsim 采集的吞吐量结果文件，从中解析出吞吐量
        :param inputFile:
        :return:
        """
        throughput = Throughput()
        with open(inputFile, "r") as f:
            # 首先忽略表头
            # Time	Node	FaceId	FaceDescr	Type	Packets	Kilobytes	PacketRaw	KilobytesRaw
            f.readline()

            # 从第一行开始解析
            line = f.readline()
            while line:
                if line.strip() != "":
                    item = ThroughputItem.parseLine(line)
                    if item:
                        if item.Node not in throughput.nodeMap:
                            throughput.nodeMap[item.Node] = NodeThroughput(item.Node)
                        throughput.nodeMap[item.Node].appendItem(item)
                line = f.readline()
        return throughput


class ThroughputExtractBase:
    def __init__(self):
        self.samplingInterval = 1.0
        self.throughputType = ThroughputType.OutData
        self.throughputTarget = ThroughputTarget.Kilobytes_KBps
        self.lpPacketHeaderSize = 0  # LpPacket 头部大小

    def setSamplingInterval(self, samplingInterval: float):
        """
        设置采样间隔 => 如果 samplingInterval = 1.0 表示绘图时，每秒采样一次
        :param samplingInterval:
        :return:
        """
        self.samplingInterval = samplingInterval
        return self

    def setThroughputType(self, throughputType: ThroughputType):
        """
        设置吞吐量类型
        :param throughputType:
        :return:
        """
        self.throughputType = throughputType
        return self

    def setThroughputTarget(self, throughputTarget: ThroughputTarget):
        """
        设置吞吐量目标
        :param throughputTarget:
        :return:
        """
        self.throughputTarget = throughputTarget
        return self

    def setLpPacketHeaderSize(self, lpPacketHeaderSize: int):
        """
        设置LpPacket头部大小
        :param lpPacketHeaderSize:
        :return:
        """
        self.lpPacketHeaderSize = lpPacketHeaderSize
        return self


class ThroughputCSVItem:
    def __init__(self, nodeName: str, faceId: int,
                 units: str, label: str, x: [float], y: [float]):
        self.nodeName = nodeName
        self.faceId = faceId
        self.units = units
        self.label = label
        self.x = x
        self.y = y


class ThroughputExport(ThroughputExtractBase):
    """
    一个用于导出数据到CSV的辅助类
    """

    def __init__(self, throughput: Throughput):
        super(ThroughputExport, self).__init__()
        self.throughput = throughput
        self.items: [ThroughputCSVItem] = []

    def select(self, nodeName: str, faceId: int, label: str = None):
        node = self.throughput.getByNode(nodeName)
        if not node:
            print("not exist node: ", node)
            return self
        if label is None:
            label = nodeName
        x, y = node.getX(faceId, samplingInterval=self.samplingInterval), \
               node.getY(faceId, self.throughputType, self.throughputTarget, self.samplingInterval,
                         self.lpPacketHeaderSize)
        self.items.append(
            ThroughputCSVItem(
                nodeName, faceId,
                ThroughputTarget.getUnit(self.throughputTarget.name),
                label,
                x,
                y
            ))
        return self

    def exportExcel(self, savePath: str):
        contents = []
        nodeNames, units, labels, xResult = [], [], [], []
        for item in self.items:
            nodeNames.append(item.nodeName)
            units.append(item.units)
            labels.append(item.label)
            if len(item.x) > len(xResult):
                xResult = item.x
        # long name
        contents.append(["Times"] + nodeNames)

        # units
        contents.append(["Second"] + units)

        # comments
        contents.append([""] + labels)

        ys = [xResult]
        # padding y
        for item in self.items:
            item.y = np.pad(item.y, (0, len(xResult) - len(item.y)), 'constant', constant_values=(0, 0))
            ys.append(np.array(item.y).T)

        dataMatrix = np.vstack(ys)

        # write datas
        for i in range(len(xResult)):
            contents.append(dataMatrix[:, i])

        df = pd.DataFrame(contents)
        df.to_excel(savePath, index=False, header=None)

    def innerParse(self, inputFile: str):
        self.throughput = Throughput.parse(inputFile)
        return self

    @staticmethod
    def parse(inputFile: str):
        return ThroughputExport(Throughput.parse(inputFile))


class ThroughputGraph(GraphBase, ThroughputExtractBase):
    """
    一个用于实现绘制吞吐量图的类
    """

    def __init__(self, throughput: Throughput):
        super(ThroughputGraph, self).__init__()
        self.throughput = throughput

    def plot(self, node: str, faceId: int, *args,
             color: str = "&&",
             linewidth: float = 2, linestyle: str = "dotted", marker: str = "&&",
             markerfacecolor: str = "none", markersize: float = 6,
             **kwargs):
        node = self.throughput.getByNode(node)
        if not node:
            print("not exist node: ", node)
            return self
        if "label" not in kwargs:
            kwargs["label"] = node.Node
        x, y = node.getX(faceId, samplingInterval=self.samplingInterval), \
               node.getY(faceId, self.throughputType, self.throughputTarget, self.samplingInterval,
                         self.lpPacketHeaderSize)
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
            return self.throughput.getByNode(nodeName)

        def getX(node: NodeThroughput, nodeId):
            return node.getX(nodeId, samplingInterval=self.samplingInterval)

        def getY(node: NodeThroughput, nodeId):
            return node.getY(nodeId, self.throughputType, self.throughputTarget, self.samplingInterval,
                             self.lpPacketHeaderSize)

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
            return self.throughput.getByNode(nodeName)

        def getX(node: NodeThroughput, nodeId):
            return node.getX(nodeId, samplingInterval=self.samplingInterval)

        def getY(node: NodeThroughput, nodeId):
            return node.getY(nodeId, self.throughputType, self.throughputTarget, self.samplingInterval,
                             self.lpPacketHeaderSize)

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
        self.throughput = Throughput.parse(inputFile)
        return self

    @staticmethod
    def parse(inputFile: str):
        return ThroughputGraph(Throughput.parse(inputFile))
