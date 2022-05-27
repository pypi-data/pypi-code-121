# -*- coding:utf-8 -*-

# UOpenCVUtil 画像処理用ビットマップクラス(UOpenCV)補助関数
# (C)Copyright 2022 Y.Endou All rights reserved

# 更新履歴
# 1.0    22/10/01    初期バージョン

# matplotlibを使うが、matplotlibのバックエンドを標準のTkAggから変えておかないとハングアップすることがある
# バックエンドには
# ['GTK3Agg', 'GTK3Cairo', 'GTK4Agg', 'GTK4Cairo', 'MacOSX', 'nbAgg', 'QtAgg', 'QtCairo', 'Qt5Agg', 'Qt5Cairo', 
#  'TkAgg', 'TkCairo', 'WebAgg', 'WX', 'WXAgg', 'WXCairo', 'agg', 'cairo', 'pdf', 'pgf', 'ps', 'svg', 'template']
# などがある。
# wxPython を使う場合は、 WXAgg を利用する
# https://code-examples.net/ja/q/3220c9  (2022/05/18)

# import matplotlib
# matplotlib.use('WXAgg')
from matplotlib import pyplot as plt

from UOpenCV import UOpenCV
# -------------------------
def showHist(cv_image, wname=None, title=None, block:bool=False):
    """ヒストグラムを描画する
    ヒストグラムはcalcHistで求めておく
    @param UOpenCV cv_image UOpenCVオブジェクト
    @param str wname ウインドウ名
    @param str title 表の名前
    @param bool block  True プロットした後に待つ  False 次の処理を実行する  Trueでないと描画がうまくできないことがある
    """
    if wname is None:
        plt.figure(cv_image.log[-1])
    else:
        plt.figure(str(wname))
    if title is not None:
        plt.title(str(title),fontname="MS Gothic") # 日本語フォントを指定しないと文字化けする
    plt.grid()

    if cv_image.kind == 'color':
        plt.plot(cv_image.dist_array[0] , color='b')
        plt.plot(cv_image.dist_array[1] , color='g')
        plt.plot(cv_image.dist_array[2] , color='r')
    else:
        plt.plot(cv_image.dist_array[0] , color='k')

    plt.show(block=block)
# -------------------------
def showDist(cv_image, wname=None, title=None, block:bool=False):
    """水平・垂直方向周辺分布を描画する
    ヒストグラムはprojection_distribution_h , projection_distribution_vで求めておく
    @param UOpenCV cv_image UOpenCVオブジェクト
    @param str wname ウインドウ名
    @param str title 表の名前
    @param bool block  True プロットした後に待つ  False 次の処理を実行する  Trueでないと描画がうまくできないことがある
    """
    if wname is None:
        plt.figure(cv_image.log[-1])
    else:
        plt.figure(str(wname))
    if title is not None:
        plt.title(str(title),fontname="MS Gothic") # 日本語フォントを指定しないと文字化けする
    plt.grid()

    if cv_image.kind == 'color':
        plt.plot(cv_image.dist_array[3], cv_image.dist_array[0], color='b')
        plt.plot(cv_image.dist_array[3], cv_image.dist_array[1], color='g')
        plt.plot(cv_image.dist_array[3], cv_image.dist_array[2], color='r')
    else:
        plt.plot(cv_image.dist_array[1], cv_image.dist_array[0], color='k')

    plt.show(block=block)
# -------------------------
def showLine(cv_image, wname=None, title=None, block:bool=False):
    """線上のデータを描画する
    データはget_line_dataで求めておく
    @param UOpenCV cv_image UOpenCVオブジェクト
    @param str wname ウインドウ名
    @param str title 表の名前
    @param bool block  True プロットした後に待つ  False 次の処理を実行する  Trueでないと描画がうまくできないことがある
    """
    if wname is None:
        plt.figure(cv_image.log[-1])
    else:
        plt.figure(str(wname))
    if title is not None:
        plt.title(str(title),fontname="MS Gothic") # 日本語フォントを指定しないと文字化けする
    plt.grid()

    if cv_image.kind == 'color':
        plt.plot(cv_image.x_axis, cv_image.value_b, color='b')
        plt.plot(cv_image.x_axis, cv_image.value_g, color='g')
        plt.plot(cv_image.x_axis, cv_image.value_r, color='r')
    else:
        plt.plot(cv_image.x_axis, cv_image.value_b, color='k')

    plt.show(block=block)
# -------------------------
def plot_lookuptable(lut, name, block:bool=False):
    """ルックアップテーブルをグラフ表示する
    @param lut ルックアップテーブル
    @param str name テーブルの名前
    @param bool block  True プロットした後に待つ  False 次の処理を実行する  Trueでないと描画がうまくできないことがある
    @usage UOpenCV.plot_lookuptable(lut,fname)
    """
    plt.figure('lookup table')
    plt.title(name,fontname="MS Gothic")
    plt.plot(lut,color='k')
    plt.show(block=block)
# -------------------------
