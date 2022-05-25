# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2022/4/20 11:31
Desc:
'''
from xgboost import XGBClassifier
import pandas as pd

df_valid = pd.read_csv("../score_ecard/data/train_test_data.csv")
df_train_data = df_valid[df_valid['train_test_tag'] == '训练集'].fillna(0).head(10000)
df_test_data = df_valid[df_valid['train_test_tag'] == '测试集'].fillna(0).head(10000)
feature_columns = df_train_data.columns[4:33].tolist()
feature_columns.extend(df_train_data.columns[36:46])
df_X = df_train_data[feature_columns]
# df_Y = df_train_data['label']
df_Y=df_train_data.apply(lambda x:x['label'] if x["report_fee"]<5000 else 2,axis=1)

params_xgb = {
            'n_estimators': 3,
            'max_depth':3,
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
clf_xgb = XGBClassifier(**params_xgb)
clf_xgb.fit(df_X, df_Y)
aa=clf_xgb.get_booster()
aa.trees_to_dataframe()
