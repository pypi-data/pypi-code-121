# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2022/5/6 18:29
Desc:
'''
import pandas as pd
from score_ecard.features.xgboost_woe import XGBoostWoe

if __name__ == '__main__':
    df_valid = pd.read_csv("../score_ecard/data/train_test_data.csv")
    df_train_data = df_valid[df_valid['train_test_tag'] == '训练集'].fillna(0).head(100000)
    df_test_data = df_valid[df_valid['train_test_tag'] == '测试集'].fillna(0).head(100000)
    feature_columns = df_train_data.columns[4:33].tolist()
    feature_columns.extend(df_train_data.columns[36:46])
    df_X = df_train_data[feature_columns]
    df_Y = df_train_data[['label', 'label_ordinary',
                          'label_serious', 'label_major', 'label_devastating', 'label_8w', 'fee_got', 'report_fee']]
    df_Y = df_Y.apply(lambda x: x['label'] if x["report_fee"] < 5000 else 1, axis=1)*2

    xgb_params = {
            'n_estimators': 2,
            'max_depth':5,
            'eta': 0.3,
            'min_child_weight': 1,
            'gamma': 0.3,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'booster': 'gbtree',
            'objective': 'binary:logistic',
            'scale_pos_weight': 1,
            'lambda': 1,
            'seed':666,
            'silent': 0,
            'eval_metric': 'auc'
        }
    xgb_woe = XGBoostWoe(xgb_params)
    df_woe_list=xgb_woe.fit(df_X,df_Y)
    bb=xgb_woe.transform(df_X)

    aa=pd.concat(df_woe_list,axis=1)
    print(aa.columns)