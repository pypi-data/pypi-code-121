# -*- coding: utf8 -*-
from .downloader import  Downloader
import sys

class HtmlRender(Downloader):
    """
    html渲染器
    """

    def __init__(self, set_mode='db', get_mode='db'):
        super(HtmlRender, self).__init__(set_mode, get_mode)
