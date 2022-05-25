from .dfFilter import  DfFilter
from .paramHandler import ParamHandler
from .dfStitcher import  DfStitcher

try:
    from . import dash_core_components as dcc
except:
    from dash import dcc


all = {DfFilter, ParamHandler, DfStitcher}