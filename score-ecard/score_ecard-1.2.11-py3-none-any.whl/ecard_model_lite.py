# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2022/4/28 15:41
Desc:
'''

import numpy as np
import pandas as pd
import random
import warnings
warnings.filterwarnings('ignore')

from sklearn.linear_model import LogisticRegression
from score_ecard import score_card
from score_ecard.util import get_weighted_std, log_step,summary_explanation,model_factor_report
from score_ecard.features.xgboost_woe import XGBoostWoe
from score_ecard.util.ecard_standardized import ECardStandardized

class ECardModel(object):
    def __init__(self, kwargs_lr=None, kwargs_xgb=None, sample_frac=1.0, cross_hierarchy=0, n_estimators=None):
        '''

        :param kwargs_lr:
        :param kwargs_xgb:
        :param sample_frac: 样本再抽样比例，样本抽样比例 = 0.6*sample_frac
        :param cross_hierarchy: 特征交叉层级，可参考参数设置为[2，3]，默认不进行特征扩展即cross_hierarchy=0
        '''
        self.params_lr = {
            "class_weight": 'balanced',
            "penalty": 'l1',
            "C": 0.2,
            "solver": 'liblinear'
        }
        self.params_xgb = {
            'n_estimators': 10,
            'max_depth':5,
            'learning_rate': 0.3,
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
        self.params_base_tree = {
            'max_depth': 3,
            'max_features': None,
            'min_samples_leaf': 0.01,
            'class_weight': "balanced",
            'random_state': 666
        }
        if kwargs_lr:
            self.params_lr.update(**kwargs_lr)
        if kwargs_xgb:
            self.params_xgb.update(**kwargs_xgb)
        self.sample_frac = sample_frac
        self.cross_hierarchy = cross_hierarchy
        self.score_ecard = None
        self.score_model = score_card.ScoreCardModel()
        random.seed(666)
        if n_estimators is None:
            self.n_estimators = self.params_xgb.get("n_estimators",100)
        else:
            self.n_estimators = n_estimators

        self.xgb_woe_model = XGBoostWoe(self.params_xgb)
        self.init_cards=[]
        self.feature_ext_info={}

    def fit(self, df_X, df_Y, sample_weight=None, df_valX:pd.DataFrame=None, df_valY:pd.DataFrame=None):
        assert df_X.shape[0] == df_Y.shape[0]
        df_y, df_y_binary= self.check_label(df_Y)
        if type(sample_weight)==type(None):
            sample_weight=df_y*0+1
        log_step("start model fitting ...")
        df_woe_list = self.xgb_woe_model.fit(df_X, df_y)
        df_cards_list = self.calc_score_card(df_woe_list, df_y_binary, sample_weight)
        self.score_ecard = self.merge_cards(df_cards_list,df_X)

        self.score_lower = self.score_ecard.groupby("field_").score_.min().sum()
        self.score_upper = self.score_ecard.groupby("field_").score_.max().sum()

    def check_label(self, df_label):
        df_Y=df_label.copy()
        if df_Y.shape[-1] == 1:
            df_Y.columns = ['label']
        if 'label' not in df_Y.columns:
            df_Y['label'] = df_Y.iloc[:,0]
        df_y = df_Y.label.astype(int)
        if df_y.unique().size>2:
            df_y_binary = df_y.apply(lambda x: 1 if x>0 else 0)
        else:
            df_y_binary = df_y
        ## test---
        if 'label_binary' in df_Y.columns:
            df_y_binary = df_Y["label_binary"]
        ## ---end
        return df_y, df_y_binary

    def calc_score_card(self, df_woe_list, df_y_binary, sample_weight):
        '''

        :param df_woe_list:
        :param df_y_binary:
        :param sample_weight:
        :return:
        '''
        woe_cards_list = self.xgb_woe_model.woe_cards.copy()
        df_woe_data = pd.concat(df_woe_list,axis=1)
        clf_lr = LogisticRegression(**self.params_lr)
        clf_lr.fit(df_woe_data, df_y_binary, sample_weight=sample_weight)

        # score_card of xgb_trees
        lr_coef = clf_lr.coef_[0]
        i = 0
        col_list = [i.columns for i in df_woe_list]
        for idx_,(icol_,df_iwoe) in enumerate(zip(col_list,woe_cards_list)):
            icol_coef_ = lr_coef[i:i+len(icol_)]
            coef_dict = dict(zip(icol_, icol_coef_))

            woe_col = [i for i in df_iwoe.columns if 'woe' in i]
            get_coef_summary = lambda x: np.sum([coef_dict.get(x['field_'] + '_' + i) * x[i] for i in woe_col])
            df_iwoe['score_'] = self.score_model.score_factor * df_iwoe.apply(get_coef_summary, axis=1)
            woe_cards_list[idx_] = df_iwoe[['field_', 'bins_', 'boundary_', 'size_', 'score_']]
            i += len(icol_)

        #  init score_card
        init_score = self.score_model.score_offset
        base_score = self.score_model.score_factor * clf_lr.intercept_[0]
        df_base_card = pd.DataFrame(
            [['init_base_score', pd.Interval(-np.inf, np.inf, closed='right'), np.inf, -1, init_score],
             ['init_model_score', pd.Interval(-np.inf, np.inf, closed='right'), np.inf, -1, base_score]
             ], columns=['field_', 'bins_', 'boundary_', 'size_', 'score_'])
        woe_cards_list.append(df_base_card)

        return woe_cards_list

    def merge_cards(self, woe_cards_list,df_trian=None):
        cards=pd.concat(woe_cards_list,axis=0).reset_index(drop=True)
        cards_boundaries = cards.groupby('field_').boundary_.agg(lambda x: sorted(set([-np.inf, np.inf] + list(x))))

        if type(df_trian)==type(None):
            df_tmp = pd.DataFrame(cards_boundaries).applymap(lambda x: 0).T
        else:
            df_tmp = df_trian.copy()
            df_tmp['init_base_score']=0
            df_tmp['init_model_score'] = 0

        bins_list = []
        for i, (col, bins) in enumerate(cards_boundaries.items()):
            data_bin = pd.cut(df_tmp.loc[:, col], bins=bins).value_counts()
            df_bin = pd.DataFrame(data_bin).sort_index().reset_index()
            df_bin.columns = ['bins_', 'size_']
            df_bin.insert(loc=0, column='field_', value=col)
            df_bin.insert(loc=2, column='boundary_', value=bins[1:])
            bins_list.append(df_bin)
        df_init_ecard = pd.concat(bins_list).reset_index(drop=True)
        del df_tmp

        df_cards_out = pd.merge(df_init_ecard,cards.set_index('field_')[['bins_', 'size_','score_']],how='left',left_on='field_',right_index=True, suffixes=("", "y"))
        idx = df_cards_out.apply(
            lambda x: True if str(x['bins_y']) != 'nan' and (x['bins_'].overlaps(x['bins_y'])) else False, axis=1)
        df_cards_out.loc[~idx, 'score_'] = 0
        df_cards_out.loc[~idx, 'size_y'] = 0
        if type(df_trian)==type(None):
            df_cards_out['size_']= df_cards_out['size_y']
        df_out = df_cards_out.groupby(['field_', 'bins_', 'boundary_'])['size_','score_'].sum().reset_index()

        return df_out


    def calc_score(self, df_card, df_data: pd.DataFrame, is_woe_feature=False):
        df_score = pd.DataFrame()
        if is_woe_feature:
            pass
        else:
            bins_dict = df_card.groupby('field_').boundary_.agg(
                lambda x: sorted(set([-np.inf, np.inf] + list(x)))).to_dict()
        for field_ in df_card.field_.unique():
            if field_ in ['init_base_score','init_model_score']:
                continue
            _card = df_card[df_card.field_ == field_]
            _card["bins_"] = _card.bins_.astype(str)
            if is_woe_feature:
                _data = df_data[field_].astype(str)
            else:
                _data = pd.cut(df_data[field_].fillna(0), bins=bins_dict.get(field_, [-np.inf, np.inf])).astype(str)
            out = pd.merge(_data,_card.set_index("bins_"),how='left',left_on=_data.name,right_index=True)
            df_score[field_] = out['score_']
        df_score['init_base_score'] = df_card[df_card.field_ == 'init_base_score']['score_'].values[0]
        df_score['init_model_score'] = df_card[df_card.field_ == 'init_model_score']['score_'].values[0]
        score = df_score.sum(axis=1).apply(lambda x: round(x,2))
        return score

    def get_importance_(self):
        df_card_info = self.score_ecard.groupby("field_").agg(
            {'size_': [("weights", lambda x: list(x))],
             'score_': [("values", lambda x: list(x))]

             }).droplevel(0, 1)
        importance_ = df_card_info.apply(lambda x: get_weighted_std(x["values"], x["weights"]), axis=1)
        importance_ = (importance_/importance_.sum()).apply(lambda x:round(x,6))
        return importance_.sort_values(ascending=False)

    def predict(self, df_data):
        df_score = self.calc_score(self.score_ecard,df_data)
        return df_score

    def predict_proba(self, df_data):
        df_score = self.predict(df_data)
        df_proba =df_score.apply(lambda x:self.score_model.score_to_probability(x))
        return df_proba

    def predict_hundred(self, df_data):
        '''
        百分制
        :param df_data:
        :return:
        '''
        df_score = self.predict(df_data)
        df_hundred =df_score.apply(lambda x:round((x-self.score_lower)/(self.score_upper-self.score_lower)*100,2))
        return df_hundred

    # 单车详细评分
    def get_single_score(self, data: dict, level_threshold=None):
        score = 0
        score_detail = {}
        df_card = self.score_ecard
        for i, row in df_card.iterrows():
            field_ = row['field_']
            bins_ = row['bins_']
            score_ = row['score_']
            if field_ in ['init_base_score', 'init_model_score']:
                v = 0
            else:
                v = data.get(field_)
            try:
                v = float(v)
            except:
                score = 0
                score_detail[field_] = '异常'
                break
            if not (v > -np.inf):
                v = 0
            if v in bins_:
                score = score + score_
                score_detail[field_] = score_
            else:
                pass

        # level
        score = round(score)
        level = -1
        total_meters = data.get('run_meters', 0)
        total_seconds = data.get('run_seconds', 0)
        if (level_threshold is not None) and (total_meters >= 2000000) and (total_seconds >= 10 * 3600):
            level = np.argwhere(np.sort(level_threshold + [score]) == score).min()

        out = {'score': score, 'level': level, 'score_detail': score_detail}
        return out

    def model_explanation(self, title=None, save_path=None,**kwargs):
        return summary_explanation(self.score_ecard, title=title, save_path=save_path,**kwargs)

    def factor_report(self, title='ecard', max_display=999, save_path=None):
        return model_factor_report(self.score_ecard, title, max_display, save_path)

    def dump(self, model_name, score_bins):
        self.score_bins=score_bins
        ecard_standardized = ECardStandardized()
        ecard_standardized.dump(self, model_name, model='all')


if __name__ == '__main__':
    df_valid = pd.read_csv("data/train_test_data.csv")
    df_train_data = df_valid[df_valid['train_test_tag'] == '训练集'].fillna(0).head(1000)
    df_test_data = df_valid[df_valid['train_test_tag'] == '测试集'].fillna(0).head(1000)
    feature_columns = df_train_data.columns[4:33].tolist()
    feature_columns.extend(df_train_data.columns[36:46])
    df_X = df_train_data[feature_columns]
    df_Y = df_train_data[['label', 'label_ordinary',
                          'label_serious', 'label_major', 'label_devastating', 'label_8w','fee_got','report_fee']]
    df_Y['label']=df_Y.apply(lambda x:x['label'] if x["report_fee"]<5000 else 2,axis=1)

    ecard = ECardModel(
        kwargs_xgb={'n_estimators':2},
    )
    ecard.fit(df_X,df_Y)
    print(ecard.get_importance_())
    print(ecard.predict(df_X))
    print(ecard.predict_hundred(df_X))
    data = df_test_data.loc[0].to_dict()
    print(ecard.get_single_score(data=data, level_threshold=[-np.inf, 400, 536, 550, 600, np.inf]))
    ecard.dump('data/aa.pkl',[-np.inf, 400, 536, 550, 600, np.inf])

    import dill
    model = dill.load(open('data/aa.pkl', "rb"))
    clf_tmp = model.get("model")
    print(model.keys())
    print(clf_tmp.get_importance_())


