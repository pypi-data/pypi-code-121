# -*- coding: utf8 -*-
from .downloader import  Downloader
import sys


class HtmlDownloader(Downloader):
    """
    html下载器
    """

    def __init__(self, set_mode='db', get_mode='db'):
        super(HtmlDownloader, self).__init__(set_mode, get_mode)
