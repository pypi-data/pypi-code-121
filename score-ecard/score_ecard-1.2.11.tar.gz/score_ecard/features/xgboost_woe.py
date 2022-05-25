# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/11/5 22:08
Desc:
'''

import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
from score_ecard.features import layered_woe as woe
from score_ecard.features import xgboost_blocks as xgb_bolcks
from score_ecard.util import progress_bar, log_step

class XGBoostWoe:
    def __init__(self, xgb_params):
        self.xgb_params = xgb_params
        self.eps = 1e-4
        self.woe_cards = []

    def fit(self,df_X,df_Y,sample_weight=None):
        '''

        :param df_X: 特征数据
        :param df_Y: 标签分类字段
        :param sample_weight:
        :return: 返回woe详细信息
        '''
        log_step("XGBoostWoe: (start) ->->->  ")
        clf_xgb = XGBClassifier(**self.xgb_params)
        clf_xgb.fit(df_X, df_Y, sample_weight=sample_weight)
        xgb_report = classification_report(df_Y, clf_xgb.predict(df_X))
        log_step("XGB-report: \n {}".format(xgb_report))

        xgb_boundaries = xgb_bolcks.get_xgboost_blocks(clf_xgb, col_name=df_X.columns)
        log_step("Total {} trees.".format(len(xgb_boundaries)))

        if len(clf_xgb.classes_)>2:
            classes_list = clf_xgb.classes_.tolist() * clf_xgb.n_estimators
        else:
            classes_list = clf_xgb.classes_.tolist()[:1] * clf_xgb.n_estimators
        assert len(classes_list)==len(xgb_boundaries)

        data = []
        for i, tree_bins in enumerate(xgb_boundaries):
            progress_bar(i,len(xgb_boundaries), is_pass=False)
            y_ = (df_Y == classes_list[i]).astype(int)
            df_woe, x = woe.get_woe_card(df_X, y_, tree_bins)
            self.woe_cards.append(df_woe)
            data.append(x)
        log_step("\nXGBoostWoe: <-<-<- (end). ")

        return data

    def transform(self, df_X, num_trees=None):
        '''

        :param df_X:
        :param num_trees: 需要转义的第i棵树，默认None表示全部的树进行woe转换
        :return:
        '''
        if num_trees is None:
            data=[]
            for woe_card in self.woe_cards:
                df_data = pd.DataFrame()
                for field_ in woe_card.field_.unique():
                    df_woe = woe_card[woe_card.field_ == field_]
                    bins_ = np.sort(list(set(df_woe.boundary_.unique().tolist() + [np.inf, -np.inf]))).tolist()
                    x_bins = pd.cut(df_X[field_], bins=bins_)
                    df_bins = pd.DataFrame(x_bins)
                    df_bins.columns = ['bins_']
                    out = pd.merge(df_bins, df_woe.set_index('bins_'), how='left', left_on='bins_', right_index=True)
                    df_data[field_+'_woe1'] = out['woe1']
                data.append(df_data)
            return data
        else:
            assert -len(self.woe_cards) <= num_trees<len(self.woe_cards)
            woe_card = self.woe_cards[num_trees]
            df_data = pd.DataFrame()
            for field_ in woe_card.field_.unique():
                df_woe = woe_card[woe_card.field_ == field_]
                bins_ = np.sort(list(set(df_woe.boundary_.unique().tolist() + [np.inf, -np.inf]))).tolist()
                x_bins = pd.cut(df_X[field_], bins=bins_)
                df_bins = pd.DataFrame(x_bins)
                df_bins.columns = ['bins_']
                out = pd.merge(df_bins, df_woe.set_index('bins_'), how='left', left_on='bins_', right_index=True)
                df_data[field_+'_woe1'] = out['woe1']

            return df_data