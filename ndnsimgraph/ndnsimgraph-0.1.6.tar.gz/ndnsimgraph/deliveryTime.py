from .common import GraphBase, getRandomColor
from .throughput import Throughput, NodeItem, ThroughputType, ThroughputTarget
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.legend import Legend
from matplotlib.patches import Patch
import matplotlib.ticker as mticker


class DeliveryTimeCollection:
    """
    分发时间集合，包含了期望从同一次实验获取的所有内容交付时间数据
    """

    def __init__(self, collectionName: str, labels: [str], colors: [str],
                 contentDeliveryTimeGroups: [[float]], hatch: str,
                 xlabels: [str]):
        """
        构造一个分发时间集合
        :param collectionName:      集合的名字，通常是方案的名字，比如 DSCCP
        :param labels:              标签列表
        :param contentDeliveryTimeGroups:   分发节点条目
        """
        self.collectionName = collectionName
        self.labels = labels
        self.colors = colors
        self.xlabels = xlabels
        self.hatch = hatch
        self.contentDeliveryTimeGroups = contentDeliveryTimeGroups


class DeliveryTimeCollectionBuilder:
    def __init__(self, collectionName: str, throughputFile: str, hatch: str = None):
        self.collectionName = collectionName
        self.throughput = Throughput.parse(throughputFile)
        self.labels = []
        self.deliveryTimeGroups = []
        self.hatch = hatch
        self.xlabels = []
        self.usedColor = []
        # 记录常用的 color
        self.colors = [
            "tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple",
            "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan", "red", "green", "blue", "c", "m", "y",
        ]
        # 记录当前图已经使用的 color
        self.currentUsedColor = {}

    def autoSelectColor(self) -> str:
        for color in self.colors:
            if color not in self.currentUsedColor:
                self.currentUsedColor[color] = color
                return color
        while True:
            randomColor = getRandomColor()
            if randomColor not in self.currentUsedColor:
                break
            self.currentUsedColor[randomColor] = randomColor
        return randomColor

    def appendDeliveryNodeItem(self, label: str, items: [NodeItem], color: str = "&&", samplingInterval=0.5,
                               throughputType: ThroughputType = ThroughputType.OutData,
                               throughputTarget: ThroughputTarget = ThroughputTarget.PacketRaw):
        self.labels.append(label)
        if color == "&&":
            color = self.autoSelectColor()
        self.usedColor.append(color)
        contentDeliveryTimes, xlabels = [], []
        for item in items:
            contentDeliveryTime = 0
            x = self.throughput.getByNode(item.nodeName).getX(item.nodeId,
                                                              samplingInterval=samplingInterval,
                                                              throughputType=throughputType)
            y = self.throughput.getByNode(item.nodeName).getY(item.nodeId,
                                                              samplingInterval=samplingInterval,
                                                              throughputType=throughputType,
                                                              throughputTarget=throughputTarget)
            if len(x) > 0:
                contentDeliveryTime = x[-1]
                for i in reversed(range(len(y))):
                    if y[i] != 0:
                        contentDeliveryTime = x[i]
                        break
            contentDeliveryTimes.append(contentDeliveryTime)
            xlabels.append(item.nodeName)
        self.xlabels.append(xlabels)
        self.deliveryTimeGroups.append(contentDeliveryTimes)
        return self

    def build(self) -> DeliveryTimeCollection:
        return DeliveryTimeCollection(self.collectionName, self.labels, self.usedColor,
                                      self.deliveryTimeGroups, self.hatch, self.xlabels)


class DeliveryTimeGraph(GraphBase):
    """
    一个用于绘制内容交付时间图的类
    1. 通过吞吐量统计数据进行判断 => 如果一个 Consumer 的吞吐量变成0了，认为内容交付完成，取该时间为内容交付时间
    """

    def __init__(self):
        super(DeliveryTimeGraph, self).__init__()
        self.deliveryTimeCollections: [DeliveryTimeCollection] = []
        self.figSize = (10, 7)  # 图的大小
        self.edgecolor = "black"  # 边缘颜色
        self.totalWidth = 1
        self.fig = None
        self.ax = None

    def setTotalWidth(self, totalWidth: float):
        self.totalWidth = totalWidth
        return self

    def appendDeliveryTimeCollection(self, deliveryTimeCollection: DeliveryTimeCollection):
        """
        添加一个内容完成时间条目
        :return:
        """
        if deliveryTimeCollection.hatch is None:
            deliveryTimeCollection.hatch = self.autoSelectHatch()
        self.deliveryTimeCollections.append(deliveryTimeCollection)
        return self

    def xlim(self, *args, **kwargs):
        self.ax.set_xlim(*args, **kwargs)
        return self

    def ylim(self, *args, **kwargs):
        plt.ylim(*args, **kwargs)
        return self

    def xticks(self, ticks=None, labels=None, **kwargs):
        plt.xticks(ticks, labels, **kwargs)
        return self

    def title(self, label, fontdict=None, loc=None, pad=None, **kwargs):
        self.ax.title(label, fontdict=fontdict, loc=loc, pad=pad, **kwargs)
        return self


    def legend(self, *args, **kwargs):
        handles, labels = self.ax.get_legend_handles_labels()
        self.ax.legend(handles, labels, *args, **kwargs)
        return self

    def categoryLegend(self, facecolor='white', *args, loc='upper left', **kwargs):
        categories, patches = [], []
        for dtc in self.deliveryTimeCollections:
            categories.append(dtc.collectionName)
            patches.append(Patch(facecolor=facecolor, edgecolor=self.edgecolor, hatch=dtc.hatch))
        if "frameon" not in kwargs:
            kwargs["frameon"] = False
        leg = Legend(self.ax, patches, categories, *args, loc=loc, **kwargs)
        self.ax.add_artist(leg)
        return self

    def doDraw(self):
        """
        绘制内容完成时间图
        :return:
        """
        maxSize, maxN = 0, 0
        for dtc in self.deliveryTimeCollections:
            if len(dtc.contentDeliveryTimeGroups[0]) > maxSize:
                maxSize = len(dtc.contentDeliveryTimeGroups[0])
            if len(dtc.contentDeliveryTimeGroups) > maxN:
                maxN = len(dtc.contentDeliveryTimeGroups)
        x = np.arange(maxSize)
        total_width, n = self.totalWidth, maxN
        width = total_width / n
        x = x - ((len(self.deliveryTimeCollections) - 1) * width / 2)

        self.fig, self.ax = plt.subplots(figsize=self.figSize)
        offsetX, isFirst =  0, True
        for dtc in self.deliveryTimeCollections:
            bottom = np.zeros(len(dtc.contentDeliveryTimeGroups[0]))
            for i in range(len(dtc.colors)):
                if isFirst:
                    self.ax.bar(x + offsetX, dtc.contentDeliveryTimeGroups[i], width=width, color=dtc.colors[i],
                                edgecolor=self.edgecolor,
                                label=dtc.labels[i],
                                bottom=bottom,
                                hatch=dtc.hatch)
                else:
                    self.ax.bar(x + offsetX, dtc.contentDeliveryTimeGroups[i], width=width, color=dtc.colors[i],
                                edgecolor=self.edgecolor,
                                bottom=bottom,
                                hatch=dtc.hatch)
                bottom += np.array(dtc.contentDeliveryTimeGroups[i])
            isFirst = False
            offsetX += width

        consumers = self.deliveryTimeCollections[0].xlabels[0]
        ticks_loc = self.ax.get_xticks().tolist()
        self.ax.xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        self.ax.set_xticklabels([""] + consumers + [""])
        return self
