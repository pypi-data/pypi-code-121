#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : sim_app
# @Time         : 2021/9/1 下午2:45
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : https://blog.csdn.net/Datawhale/article/details/107053926
# http://cw.hubwiz.com/card/c/streamlit-manual/1/6/50/

import wget
import zipfile

import streamlit as st

from meutils.pipe import *
from meutils.log_utils import logger4wecom
from bertzoo.simbert2vec import Simbert2vec
from gensim.models import KeyedVectors
