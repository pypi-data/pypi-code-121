#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: 信号动作

import signal
from threading import Event

stop_event = Event()

def handle_sigint(signum, frame):
    stop_event.set()

signal.signal(signal.SIGINT, handle_sigint)
