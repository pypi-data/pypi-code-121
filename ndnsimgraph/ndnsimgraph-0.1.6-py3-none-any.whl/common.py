import os
import random
import matplotlib.pyplot as plt
import numpy as np


def getRandomColor():
    """获取一个随机的颜色"""
    colorArr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0, 14)]
    return "#" + color


class NodeItem:
    def __init__(self, nodeName, nodeId):
        self.nodeName = nodeName
        self.nodeId = nodeId


class GraphBase:
    """
    一个基于 matplotlib 实现的通用绘图接口
    """

    def __init__(self):
        # 记录所有可用的 Marker
        # https://matplotlib.org/stable/api/markers_api.html
        self.markers = ["o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h", "H", "+",
                        "x", "X", "D", "d", "|", "_", ".", ","]
        # 记录当前图已经使用的Marker
        self.currentUsedMarker = {}
        # 记录常用的 color
        self.colors = [
            "tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple",
            "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan", "red", "green", "blue", "c", "m", "y",
        ]
        # 记录当前图已经使用的 color
        self.currentUsedColor = {}
        # 记录常用的 hatch
        self.hatches = ['', '/', 'o', '\\', 'O', '|', '-', '+', 'x', '.', '*',
                        '/o', '\\|', '|*', '-\\', '+o', 'x*', 'o-', 'O|', 'O.', '*-']
        self.currentUsedHatch = {}

    def autoSelectHatch(self) -> str:
        """
        从所有的候选 Hatch 中自动选择
        :return:
        """
        for hatch in self.hatches:
            if hatch not in self.currentUsedHatch:
                self.currentUsedHatch[hatch] = hatch
                return hatch
        return ""

    def autoSelectMarker(self) -> str:
        """
        从所有的marker中自动选择 Marker，保证不和已有的Marker重复
        :return:
        """
        for marker in self.markers:
            if marker not in self.currentUsedMarker:
                self.currentUsedMarker[marker] = marker
                return marker
        return ""

    def autoSelectColor(self) -> str:
        for color in self.colors:
            if color not in self.currentUsedColor:
                return color
        while True:
            randomColor = getRandomColor()
            if randomColor not in self.currentUsedColor:
                break
            self.currentUsedColor[randomColor] = randomColor
        return randomColor

    def xlim(self, *args, **kwargs):
        plt.xlim(*args, **kwargs)
        return self

    def ylim(self, *args, **kwargs):
        plt.ylim(*args, **kwargs)
        return self

    def xticks(self, ticks=None, labels=None, **kwargs):
        plt.xticks(ticks, labels, **kwargs)
        return self

    def title(self, label, fontdict=None, loc=None, pad=None, **kwargs):
        plt.title(label, fontdict=fontdict, loc=loc, pad=pad, **kwargs)
        return self

    def xlabel(self, xlabel, fontdict=None, labelpad=None, loc=None, **kwargs):
        plt.xlabel(xlabel, fontdict, labelpad, loc=loc, **kwargs)
        return self

    def ylabel(self, ylabel, fontdict=None, labelpad=None, loc=None, **kwargs):
        plt.ylabel(ylabel, fontdict, labelpad, loc=loc, **kwargs)
        return self

    def legend(self, *args, **kwargs):
        plt.legend(*args, **kwargs)
        return self

    def innerPlot(self, x, y, *args,
                  color: str = "&&",
                  linewidth: float = 2, linestyle: str = "dotted", marker: str = "&&",
                  markerfacecolor: str = "none", markersize: float = 6,
                  **kwargs):
        if "linewidth" not in kwargs:
            kwargs["linewidth"] = linewidth
        if "linestyle" not in kwargs:
            kwargs["linestyle"] = linestyle
        # 默认自动选择Marker
        if marker == "&&":
            marker = self.autoSelectMarker()
            self.currentUsedMarker[marker] = marker
        if "marker" not in kwargs:
            kwargs["marker"] = marker
        if "markerfacecolor" not in kwargs:
            kwargs["markerfacecolor"] = markerfacecolor
        if "markersize" not in kwargs:
            kwargs["markersize"] = markersize
        # 默认自动选择 color
        if color == "&&":
            color = self.autoSelectColor()
            self.currentUsedColor[color] = color
        if "color" not in kwargs:
            kwargs["color"] = color
        plt.plot(x, y, *args, **kwargs)
        return self

    def innerPlotSum(self, nodeList: [NodeItem], getNode, getX, getY, *args,
                     color: str = "&&",
                     linewidth: float = 2, linestyle: str = "dotted", marker: str = "&&",
                     markerfacecolor: str = "none", markersize: float = 6,
                     **kwargs):
        xMerge = []
        yArr = []
        for nodeItem in nodeList:
            node = getNode(nodeItem.nodeName)
            if not node:
                print("not exist node: ", node)
                continue

            x, y = getX(node, nodeItem.nodeId), \
                   getY(node, nodeItem.nodeId)

            if len(x) > len(xMerge):
                xMerge = x
            yArr.append(np.array(y))

        if len(yArr) <= 0:
            return self

        yMerge = np.zeros(len(xMerge))
        # pad y
        for y in yArr:
            y = np.pad(y, (0, len(xMerge) - len(y)), 'constant', constant_values=(0, 0))
            yMerge += y

        if "label" not in kwargs:
            kwargs["label"] = "Merge"

        self.innerPlot(xMerge, yMerge, *args,
                       color=color,
                       linewidth=linewidth,
                       linestyle=linestyle,
                       marker=marker,
                       markerfacecolor=markerfacecolor,
                       markersize=markersize,
                       **kwargs)
        return self

    def innerPlotAvg(self, nodeList: [NodeItem], getNode, getX, getY, *args,
                     color: str = "&&",
                     linewidth: float = 2, linestyle: str = "dotted", marker: str = "&&",
                     markerfacecolor: str = "none", markersize: float = 6,
                     **kwargs):
        xMerge = []
        yArr = []

        for nodeItem in nodeList:
            node = getNode(nodeItem.nodeName)
            x, y = getX(node, nodeItem.nodeId), \
                   getY(node, nodeItem.nodeId)
            if not node:
                print("not exist node: ", node)
                continue
            if len(x) > len(xMerge):
                xMerge = x
            yArr.append(np.array(y))

        if len(yArr) <= 0:
            return self

        yMerge = np.zeros(len(xMerge))

        # pad y
        for y in yArr:
            y = np.pad(y, (0, len(xMerge) - len(y)), 'constant', constant_values=(0, 0))
            yMerge += y
        yMerge /= len(yArr)

        if "label" not in kwargs:
            kwargs["label"] = "Merge"

        self.innerPlot(xMerge, yMerge, *args,
                       color=color,
                       linewidth=linewidth,
                       linestyle=linestyle,
                       marker=marker,
                       markerfacecolor=markerfacecolor,
                       markersize=markersize,
                       **kwargs)
        return self

    def show(self, *args, **kwargs):
        """
        绘制吞吐量图，并show
        :return:
        """
        plt.show(*args, **kwargs)
        return self

    def drawAndSave(self, dir: str, name: str, *args, **kwargs):
        """
        绘制吞吐量图，并保存到图片当中
        :return:
        """
        if not os.path.exists(dir):
            os.makedirs(dir)
        plt.savefig(f"{dir}{os.sep}{name}", *args, **kwargs)
        return self

    def close(self):
        plt.close()
