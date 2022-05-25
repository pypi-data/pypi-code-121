#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   confusion_seaborn.py    
@Contact :   544855237@qq.com

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/12/20 下午3:56   qiufengfeng      1.0         None
'''

# import lib
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

sns.set_style({"font.sans-serif":['SimHei','Arial']})


def plot_confusion_mat(gold_lables,pred_labels,labels,title="混淆矩阵",normalize=None):
    """
    @param gold_lables:真实样本
    @param pred_labels:预测样本
    @param labels:预测标签样本
    @param title:生成的图片标题
    @return:
    """
    plt.figure(figsize=(len(labels),len(labels)))
    _confmat = confusion_matrix(gold_lables,pred_labels,normalize=normalize)
    print(_confmat)
    if normalize is not None:
        _heatmap = sns.heatmap(_confmat,vmax=1,vmin=0,square=True,annot=True,cmap='Blues',xticklabels=labels,yticklabels=labels,fmt='g')
    else:
        _heatmap = sns.heatmap(_confmat,square=True,annot=True,cmap='Blues',xticklabels=labels,yticklabels=labels,fmt='g')
    _heatmap.tick_params(which='major', labelbottom=False, labeltop=True)
    figure = _heatmap.get_figure()
    figure.show()
    return figure

