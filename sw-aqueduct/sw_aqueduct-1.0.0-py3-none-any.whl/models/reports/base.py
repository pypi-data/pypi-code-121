# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import typing

from attr import define, field


@define
class ColorMap:
    name: typing.AnyStr = field()
    value: typing.AnyStr = field()
    isInternal: bool = field()


@define
class SortEntries:
    name: typing.AnyStr = field()


@define
class Sort:
    directionD0: typing.AnyStr = field()
    directionD1: typing.AnyStr = field()
    entriesD0: typing.List[SortEntries] = field(default=[])
    entriesD1: typing.List[SortEntries] = field(default=[])


@define
class ChartOptions:
    colorScheme: typing.AnyStr = field()
    showLegend: bool = field()
    legendPosition: int = field()
    showLabels: bool = field()
    showXAxis: bool = field()
    showXAxisLabel: bool = field()
    showYAxis: bool = field()
    showYAxisLabel: bool = field()
    gradient: bool = field()
    zoom: bool = field()
    autoScale: bool = field()
    explodeSlices: bool = field()
    transparentBackground: bool = field()
    sort: Sort = field()
    showOtherGroup: bool = field()
    showAxis: bool = field()
    min: int = field()
    max: int = field()
    minRadius: int = field()
    maxRadius: int = field()
    units: typing.AnyStr = field()
    bigSegments: int = field()
    smallSegments: int = field()
    angleSpan: int = field()
    startAngle: int = field()
    value: int = field()
    code: typing.AnyStr = field()
    yAxisLabelText: typing.AnyStr = field()
    xAxisLabelText: typing.AnyStr = field()
