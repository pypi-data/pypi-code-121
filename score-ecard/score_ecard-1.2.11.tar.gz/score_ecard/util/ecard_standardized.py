# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2022/3/21 14:55
Desc:
'''
import pandas as pd
import numpy as np
import dill

class ECardStandardized(object):
    def __init__(self):
        self.clf = None
        self.score_card = None
        self.score_bins = None
        self.card_ext = pd.DataFrame()

    def load(self, model_name:str):
        model = dill.load(open(model_name, "rb"))
        self.clf = model.get('model')
        self.score_card  = model.get('score_card')
        self.score_bins = model.get('score_bins',[])
        self.card_ext = model.get('features_ext',pd.DataFrame())
        self.info = model.get('info','')

        self.preprocessing_befor = model.get('preprocessing_befor',self.func_empty)
        self.preprocessing_after = model.get('preprocessing_after',self.func_empty)
        self.postprocessing = model.get('postprocessing',self.get_g7_level)

    def dump(self, clf_model, model_name, model='all'):
        assert model in ['all','pure'],'all for backup, pure for online'
        score_card = clf_model.score_ecard
        card_ext = clf_model.feature_ext_info.get("df_ext",pd.DataFrame())
        assert hasattr(clf_model,'score_bins'), "need to set 'clf_model.score_bins=[]' for score_level"
        score_bins = clf_model.score_bins
        if hasattr(clf_model, 'info'):
            info = clf_model.info
        else:
            info = ""
        if model =='pure':
            model_raw = None
        else:
            model_raw = clf_model
        model = {
            'model': model_raw,
            'score_card': score_card,
            'features_ext': card_ext,
            'score_bins': score_bins,
            'info': info
        }
        dill.dump(model, open(model_name, "wb"), protocol=3)

    def predict(self,data):
        score_info = self.get_single_score(data)
        return score_info

    def get_single_score(self, data=None):
        if data is None:
            data = {}
        data = self.preprocessing_befor(data)
        data = self.get_ext_features(data)
        data = self.preprocessing_after(data)
        score = 0
        score_detail = {}
        for i, row in self.score_card.iterrows():
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
        score = round(score,2)
        level = np.argwhere(np.sort(self.score_bins + [score]) == score).min()

        # level
        score,level = self.postprocessing(data,score,level)
        out = {'card_score': score, 'card_level': level, 'score_detail': score_detail}
        return out

    def get_ext_features(self, raw_data):
        data = raw_data.copy()
        df_ext = self.card_ext.copy()
        ext_columns = [col_ for col_ in df_ext.columns if 'ext-' in col_]
        for icol in ext_columns:
            colinfo = str(icol).split('-')
            if 'ext' == colinfo[0]:
                idx_equ = True
                for jcol in colinfo[1:]:
                    if jcol not in df_ext.columns:
                        break
                    idx_equ = idx_equ & df_ext[jcol].apply(lambda _: data.get(jcol) in _).astype(bool)
                value_ = df_ext.loc[idx_equ, icol].values
                if len(value_) > 0:
                    data.update({icol: value_[0]})
                else:
                    data.update({icol: 0})
        return data

    def func_empty(self,x):
        return x

    def get_g7_level(self,data, score, level):
        total_meters = data.get('run_meters', 0)
        total_seconds = data.get('run_seconds', 0)
        if (total_meters < 2000000) or (total_seconds < 10 * 3600):
            level = -1
        if score<=0:
            level = -1
        return score,level

if __name__ == '__main__':
    model_name = "../data/score_card_model_online_o2o_tangshan_v3.2.0.pkl"
    ecard = ECardStandardized()
    ecard.load(model_name)

    data = {
        'carnum': 'LBZ447DB1KA009342',
        'trip_cnt': 143,
        'run_meters': 12275107.380000005,
        'run_seconds': 771092,
        'trip_avg_meters': 85839.91174825176,
        'trip_avg_seconds': 5392.251748251748,
        'trip_avg_distance': 44253.81818181818,
        'high_meters_ratio': 0.002143811796129477,
        'province_meters_ratio': 0.34486200315422405,
        'high_trip_cnt_ratio': 0.0,
        'province_trip_cnt_ratio': 0.5874125874125874,
        'curvature_g2_trip_meters_ratio': 0.5600617817161611,
        'ng_23_6_seconds_ratio': 0.2924709373200604,
        'ng_23_6_trip_cnt_ratio': 0.4335664335664336,
        'daily_run_kmeters': 84.41548247018672,
        'daily_run_hours': 1.4729923918800238,
        'daily_trip_cnt': 0.9834059792344316,
        'daily_nohigh_kmeters': 84.23451156309116,
        'daily_ng_23_6_hours': 0.43080746551846827,
        'trip_long_cnt_ratio': 0.0,
        'day_high_meters_ratio': 0.0017513956769965135,
        'ng_province_meters_ratio': 0.10545102620519804,
        'morn_6_10_seconds_ratio': 0.13508245449310846,
        'dusk_17_20_seconds_ratio': 0.19514792009254409,
        'ng_23_6_avg_speed': 60.85796919147581,
        'morn_6_10_avg_speed': 55.72396178992139,
        'dusk_17_20_avg_speed': 51.151944177515524,
        'low_speed_seconds_ratio': 0.3662662821038216,
        'low_speed_block_cnt_ratio': 0.2351517298382336,
        'week_1_5_seconds_ratio': 0.29913551171585234,
        'geohash4_top10_meters_ratio': 0.9702472802319388,
        'trip_r30m_cnt_ratio': 0.4795918367346938,
        'common_line_top30_cnt_ratio': 0.030769230769230767,
        'mil_ratio_province_hb': 1.0,
        'mil_ratio_province_tj': 0.0,
        'mil_ratio_province_else': 0.0,
        'mil_ratio_city_ts': 1.0,
        'mil_ratio_city_around': 0.0,
        'mil_ratio_city_else': 0.0,
        'mil_ratio_county_west': 0.0015470292366599212,
        'mil_ratio_county_south': 0.5677351500284784,
        'mil_ratio_county_east': 0.2494958703978352,
        'mil_ratio_county_else': 0.18122195033702654,
        'top1_city_mileage_rate': 1.0,
        'top2_city_mileage_rate': 1.0,
        'top1_province_mileage_rate': 1.0,
        'top2_province_mileage_rate': 1.0,
        'top1_county_mileage_rate': 0.3229254357854749,
        'top2_county_mileage_rate': 0.5677351500284797,
        'ratio_nonglinmufu': 0.0290325496489345,
        'ratio_meitan': 0.0006003401293231343,
        'ratio_gangtie': 0.1395834542570436,
        'ratio_shashi': 0.017055577543834046,
        'ratio_kuaidi': 0.08425476464525228,
        'ratio_jiadian': 0.004164982562417855,
        'ratio_fengdian': 0.0,
        'ratio_jixie': 0.6604690662393785,
        'ratio_qiche': 0.0006478740548063132,
        'ratio_other': 0.06419139091900974,
        'pred': '机械',
        'triggertime': '2021-04-02 02:35:52',
        'triggertime_end': '2021-08-29 22:33:06',
        'source': 10
     }
    out = ecard.predict(data)
    print(out)