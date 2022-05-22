# -*- coding: utf-8 -*-
"""
Created on April 13,  2022

@author: wang Haihua
"""

from importlib_metadata import entry_points
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import math
plt.rcParams.update({'font.family': 'SimHei', 'mathtext.fontset': 'stix'})

###########################################################################################
###############################     1 Radar plot       ###############################
###########################################################################################

####***************************     1.1 Normalization       ****************************###

def radar_plot(df,plot_package='matplotlib',savefig=False,save_path='radar.png'):
    """ Draw a radar plot based on the given data with the type of pandas DataFrame

    Parameters
    ----------
    df           : a pandas object that contains specific columns

    plot_package : type of plotting package
        - 'matplotlib'(default)
        - 'plotly'

    savefig      : whether save the figure

    save_path    : where to save the figure

        
    Yields
    ------
    fig          : the radar plot

    """
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    names = list(df.index)
    labels = list(df.columns)
    data = [dict(df.loc[names[i],:]) for i in range(len(names))]
    data_length = len(data[0])
    # 将极坐标根据数据长度进行等分
    angles = np.linspace(0, 2*np.pi, data_length, endpoint=False)

    score = [[v for v in d.values()] for d in data]

    # 设置图形的大小
    fig = plt.figure(figsize=(8, 6), dpi=100)
    # 新建一个子图
    ax = plt.subplot(111, polar=True)
    angles = np.concatenate((angles, [angles[0]]))
    labels = np.concatenate((labels, [labels[0]])) 
    for i in range(len(names)):
        score1 = np.concatenate((score[i],[score[i][0]]))
        # 绘制雷达图
        ax.plot(angles, score1)
    ax.set_rlim(df.values.min(), df.values.max())   
    # 设置雷达图中每一项的标签显示
    ax.set_thetagrids(angles*180/np.pi, labels)
    plt.legend(names)
    #plt.show()
    
    return fig



