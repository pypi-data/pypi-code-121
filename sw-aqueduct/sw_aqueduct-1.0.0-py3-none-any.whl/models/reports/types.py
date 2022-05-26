# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import typing

from attr import define, field, validators

from .base import ChartOptions, ColorMap


@define
class Area(ChartOptions):
    chartType: typing.AnyStr = field(validator=validators.in_(["area"]))
    curveType: typing.AnyStr = field(validator=validators.in_(["Monotone X"]))
    colorMap: typing.List[ColorMap] = field(default=[])


@define
class AdvancedPie(ChartOptions):
    chartType: typing.AnyStr = field(validator=validators.in_(["advancedPie"]))
    curveType: typing.AnyStr = field(validator=validators.in_(["Linear"]))
    colorMap: typing.List[ColorMap] = field()


@define
class Heat(ChartOptions):
    chartType: typing.AnyStr = field(validator=validators.in_(["heat"]))
    curveType: typing.AnyStr = field(validator=validators.in_(["Linear"]))
    colorMap: typing.List[ColorMap] = field()


@define
class HorizontalBar(ChartOptions):
    chartType: typing.AnyStr = field(validator=validators.in_(["horizontalBar"]))
    curveType: typing.AnyStr = field(validator=validators.in_(["Linear"]))
    colorMap: typing.List[ColorMap] = field()


@define
class Line(ChartOptions):
    chartType: typing.AnyStr = field(validator=validators.in_(["line"]))
    curveType: typing.AnyStr = field(validator=validators.in_(["Minotone X"]))
    colorMap: typing.List[ColorMap] = field()


@define
class LinearGauge(ChartOptions):
    chartType: typing.AnyStr = field(validator=validators.in_(["linearGauge"]))
    curveType: typing.AnyStr = field(validator=validators.in_(["Linear"]))
    colorMap: typing.List[ColorMap] = field(default=[])


@define
class Number(ChartOptions):
    chartType: typing.AnyStr = field(validator=validators.in_(["number"]))
    curveType: typing.AnyStr = field(validator=validators.in_(["Linear"]))
    colorMap: typing.List[ColorMap] = field()


@define
class PieGrid(ChartOptions):
    chartType: typing.AnyStr = field(validator=validators.in_(["pie"]))
    chartSubType: typing.AnyStr = field(validator=validators.in_(["pieGrid"]))
    curveType: typing.AnyStr = field(validator=validators.in_(["Linear", "Cardinal Closed"]))
    colorMap: typing.List[ColorMap] = field()


@define
class VerticalBar(ChartOptions):
    chartType: typing.AnyStr = field(validator=validators.in_(["verticalBar"]))
    curveType: typing.AnyStr = field(validator=validators.in_(["Linear"]))
    colorMap: typing.List[ColorMap] = field(default=[])


@define
class Widget(ChartOptions):
    chartType: typing.AnyStr = field(validator=validators.in_(["widget"]))
    curveType: typing.AnyStr = field(validator=validators.in_(["Linear"]))
    colorMap: typing.List[ColorMap] = field(default=[])
