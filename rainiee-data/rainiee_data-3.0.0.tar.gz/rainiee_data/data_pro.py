# -*- coding:utf-8 -*-
from rainiee_data.base import client, login, upass
import pandas as pd

def auth(username=None, password=None):
    upass.set_token(login.LoginApi(username, password).login())

def get_client():
    return client.DataApi(upass.get_token())

def cn_index_eod(index_code, start_index, end_index):
    return pd.DataFrame(get_client().query(api_name='cn_index_eod',method_type='POST', req_param={
        'index_code': index_code,
        'start_index': start_index,
        'end_index': end_index
    }))

def cn_index_composition(index_code):
    return get_client().query(api_name='cn_index_composition',method_type='POST', req_param={
        'index_code': index_code
    })

def cn_index_composition_weight(index_code):
    return pd.DataFrame(get_client().query(api_name='cn_index_composition_weight',method_type='POST',  req_param={
        'index_code': index_code
    }))


def cn_index_basic(market):
    return  pd.DataFrame(get_client().query(api_name='cn_index_basic',method_type='POST',   req_param={
        'market': market
    }))

def cn_symbol_list(category):
    return get_client().query(api_name='cn_symbol_list',method_type='POST',   req_param={
        'category': category
    })

def cn_stock_eod(symbol, start_index, end_index,adj='qfq',frequency='D'):
    return pd.DataFrame(get_client().query(api_name='cn_stock_eod',method_type='POST', req_param={
        'symbol': symbol,
        'start_index': start_index,
        'end_index': end_index,
        'adj':adj,
        'frequency':frequency
    }))

def cn_stock_realtime(symbol):
    return get_client().query(api_name='cn_stock_realtime',method_type='POST', req_param={
        'symbol': symbol
    })

def get_trade_index(date):
    return get_client().query(api_name='get_trade_index',method_type='POST', req_param={'date': date if isinstance(date, str) else date.strftime('%Y%m%d')})


def get_trade_date(index):
    return get_client().query(api_name='get_trade_date',method_type='POST', req_param={'index': index})


def cn_features_eod(symbol, start_index, end_index):
    return pd.DataFrame(get_client().query(api_name='cn_features_eod',method_type='POST', req_param={
        'symbol': symbol,
        'start_index': start_index,
        'end_index': end_index
    }))

def cn_targets_eod(symbol, start_index, end_index):
    return pd.DataFrame(get_client().query(api_name='cn_targets_eod',method_type='POST', req_param={
        'symbol': symbol,
        'start_index': start_index,
        'end_index': end_index
    }))


def cn_stock_eod_odps(symbol, start_index, end_index):
    return pd.DataFrame(get_client().query(api_name='cn_stock_eod_odps',method_type='POST', req_param={
        'symbol': symbol,
        'start_index': start_index,
        'end_index': end_index
    }))


def cn_stock_factor_odps(symbol,factor, start_index, end_index):
    return pd.DataFrame(get_client().query(api_name='cn_stock_factor_odps',method_type='POST', req_param={
        'factor': factor,
        'symbol': symbol,
        'start_index': start_index,
        'end_index': end_index
    }))

def get_top_returns(index_code,index,top=10):
    return get_client().query(api_name='get_top_returns',method_type='POST', req_param={
        'index_code': index_code,
        'index': index,
        'top': top
    })