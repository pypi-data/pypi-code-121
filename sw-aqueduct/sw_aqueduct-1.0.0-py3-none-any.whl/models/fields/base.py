# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import typing

from attr import define, field


@define
class BaseField:
    name: typing.AnyStr = field()
    id: typing.AnyStr = field(eq=False, order=False)
    key: typing.AnyStr = field()
