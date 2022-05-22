import matplotlib.pyplot as plt
import numpy as np

from .reducedraw import reducedraw



def altitude_plot(func, x,tx,ty, altitude=0.1,inc=0.0, hist=True):
    reducedraw(x,tx,ty,func,altitude,inc=inc, hist=hist)



