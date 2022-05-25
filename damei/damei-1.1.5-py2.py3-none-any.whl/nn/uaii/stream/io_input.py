"""
模块的io，模块有输入流和输入流，每个流都有队列
"""
import os, sys
import time
import damei as dm
from ..registry import MODULES, SCRIPTS, IOS
from .queue import AbstractQue


class AbstractInput(object):
    name = 'default name'
    status = 'stopped'
    description = 'default description'

    def __init__(self, maxlen=5, *args, **kwargs):
        self.que = AbstractQue(maxlen, *args, **kwargs)


@IOS.register_module(name='visible_input')
class VisInputStream(AbstractInput):
    name = 'visible_input'
    description = '可见光数据输入流'

    def __init__(self, m_cfg, *args, **kwargs):
        self.m_cfg = m_cfg  # 自己所属模块的配置
        self.cfg = m_cfg.input_stream  # 自己的cfg
        que = self.cfg.get('que', dict())
        maxlen = que.get('maxlen', 5)
        super(VisInputStream, self).__init__(maxlen=maxlen, *args, **kwargs)

