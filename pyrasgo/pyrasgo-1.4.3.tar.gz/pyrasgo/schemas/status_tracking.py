#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel


class StatusTracking(BaseModel):
    tracking_uuid: str
    message: Optional[str] = None
    status: str
