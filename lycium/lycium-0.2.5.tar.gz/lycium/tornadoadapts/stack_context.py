#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import contextvars

def wrap(callback):
    ctx = contextvars.copy_context()
    ctx.run(callback)
