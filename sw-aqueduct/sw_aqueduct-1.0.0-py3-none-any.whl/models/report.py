# -*- coding: utf-8 -*-
from typing import AnyStr, List

from attr import define, field

# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from .reports import (
    AdvancedPie,
    Area,
    Heat,
    HorizontalBar,
    Line,
    LinearGauge,
    Number,
    PieGrid,
    VerticalBar,
    Widget,
)


@define
class GroupBys:
    fieldId: AnyStr = field()
    groupByType: AnyStr = field()


@define
class Aggregates:
    fieldId: AnyStr = field()
    aggregateType: AnyStr = field()


@define
class Filters:
    fieldId: AnyStr = field()
    filterType: AnyStr = field()
    drillin: bool = field()
    value: AnyStr = field(default=None)


@define
class Report:
    applicationIds: List = field()
    columns: List = field()
    sorts: dict = field()
    filters: List[Filters] = field()
    countByApplicationFacet: bool = field()
    pageSize: int = field()
    offset: int = field()
    defaultSearchReport: bool = field()
    permissions: dict = field(eq=False)
    modifiedDate: AnyStr = field(eq=False)
    createdByUser: dict = field(eq=False)
    modifiedByUser: dict = field(eq=False)
    uid: AnyStr = field(eq=False)
    version: int = field(eq=False)
    id: AnyStr = field()
    name: AnyStr = field()
    disabled: bool = field()
    chartOptions = field(default={})
    groupBys: List[GroupBys] = field(default=[])
    aggregates: List[Aggregates] = field(default=[])
    allowed: List = field(default=[])
    statsDrillin: bool = field(default=None)
    createdDate: AnyStr = field(default=None, eq=False)
    keywords: AnyStr = field(default=None)

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="Report")

    def __attrs_post_init__(self):
        if self.chartOptions:
            for item in [
                Area,
                AdvancedPie,
                Heat,
                HorizontalBar,
                Line,
                LinearGauge,
                Number,
                PieGrid,
                VerticalBar,
                Widget,
            ]:
                try:
                    self.chartOptions = item(**self.chartOptions)
                except Exception as e:
                    continue
