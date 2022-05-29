"""Simple script of pema to load requested modules"""
import socket
import strax
import straxen
import wfsim
import os
import pandas as pd
import numba
import time
import numpy as np
import pema
import json
import nestpy
from tqdm.notebook import tqdm
# Use nice fancy tqdm for simulating
wfsim.core.tqdm = tqdm
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import multihist
from scipy.stats import norm
from collections import defaultdict

straxen.print_versions(['strax', 'straxen', 'wfsim', 'nestpy', 'ntauxfiles', 'pema'])

# Change the plots to have style and fashion
# Updated
params = {'axes.grid': True, 'font.size': 12,
          'axes.titlesize': 16, 'axes.labelsize': 14, 'axes.linewidth': 2,
          'xtick.labelsize': 14, 'ytick.labelsize': 14,
          'ytick.major.size': 8, 'ytick.minor.size': 4,
          'xtick.major.width': 2, 'xtick.minor.width': 2,
          'ytick.major.width': 2, 'ytick.minor.width': 2,
          'xtick.direction': 'in', 'ytick.direction': 'in',
          'legend.fontsize': 14, 'figure.facecolor': 'w',
          'figure.figsize': (10, 6),
          'lines.linewidth': 2,
          'image.cmap': 'plasma'}
plt.rcParams.update(params)
