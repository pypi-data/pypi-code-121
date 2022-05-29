"""Prep __main__.py.

https://share.streamlit.io/deploy
    Advanced settings...
        Python version
            3.7
            3.8
            3.9*
            3.10

https://docs.streamlit.io/knowledge-base/using-streamlit/hide-row-indices-displaying-dataframe
    Hide row indices when displaying a dataframe
# CSS to inject contained in a string
hide_table_row_index = '''
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            '''
# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)

# Display a static table
st.table(df)

# Hide row indices with st.dataframe
# CSS to inject contained in a string
hide_dataframe_row_index = '''
            <style>
            .row_heading.level0 {display:none}
            .blank {display:none}
            </style>
           '''
# Inject CSS with Markdown
st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

# Display an interactive table
st.dataframe(df)

https://medium.com/@avra42/streamlit-python-cool-tricks-to-make-your-web-application-look-better-8abfc3763a5b
hide_menu_style = '''
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        '''
st.markdown(hide_menu_style, unsafe_allow_html=True)

"""
# pylint: disable=invalid-name
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

import loguru
import logzero
import pandas as pd
import streamlit as st
from loguru import logger as loggu
from logzero import logger
from set_loglevel import set_loglevel
from streamlit import session_state as state

from litbee import __version__, litbee
from litbee.options import options

# from litbee.files2df import files2df
# from litbee.utils import sb_front_cover, instructions, menu_items
# from litbee.ezbee_page import ezbee_page
# from litbee.dzbee_page import dzbee_page
# from litbee.xbee_page import xbee_page
from litbee.utils import menu_items

# from ezbee import ezbee

os.environ["TZ"] = "Asia/Shanghai"
time.tzset()
os.environ["LOGLEVEL"] = "10"  # uncomment this in dev
logzero.loglevel(set_loglevel())

loggu.remove()
_ = (
    "<green>{time:YY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <5}</level> | <level>{message}</level> "
    "<cyan>{name}</cyan>:<cyan>{line}</cyan>"
)
loggu.add(
    sys.stderr,
    format=_,
    level=set_loglevel(),
    colorize=True,
)

# from PIL import Image
# page_icon=Image.open("icon.ico"),
st.set_page_config(
    page_title=f"litbee v{__version__}",
    # page_icon="🧊",
    page_icon="🐝",
    # layout="wide",
    initial_sidebar_state="auto",  # "auto" or "expanded" or "collapsed",
    menu_items=menu_items,
)

# pd.set_option("precision", 2)
pd.set_option("display.precision", 2)
pd.options.display.float_format = "{:,.2f}".format

_ = dict(
    beetype="ezbee",
    src_filename="",
    tgt_filename="",
    src_fileio=b"",
    tgt_fileio=b"",
    src_file="",
    tgt_file="",
    list1=[""],
    list2=[""],
    df=None,
    df_a=None,
    df_s_a=None,
)
if "ns" not in state:
    state.ns = SimpleNamespace(**_)
state.ns.list = [*_]


def main():
    """Bootstrap."""
    options()


main()
