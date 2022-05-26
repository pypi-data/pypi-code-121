# -*- coding: utf-8 -*-
from typing import AnyStr

# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from attr import define, field


@define
class SharedBase:
    id: AnyStr = field()
    name: AnyStr = field()


@define
class CreatedByUser(SharedBase):
    pass
