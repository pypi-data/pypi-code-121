import pdb
import pandas as pd
import numpy as np

class Stock():
    @classmethod
    def _split(cls, result, name):
        columns = result[name]['columns']
        items = result[name]['items']
        data = pd.DataFrame.from_dict(items, orient='columns')
        if data.empty:
            return pd.DataFrame(columns=columns)
        data.columns=columns
        return data
    
    @classmethod
    def basic(cls, result):
        return pd.DataFrame.from_dict([result['basic_info']])
    
    @classmethod
    def flowmoeny(cls, result):
        data = cls._split(result, 'flowmoney_info')
        data['trade_date'] = pd.to_datetime(data['trade_date'])
        return data.sort_values(by='trade_date').reset_index(drop=True).set_index('trade_date')
    
    @classmethod
    def sentiment(cls, result):
        data = cls._split(result, 'sentiment_info')
        data['trade_date'] = pd.to_datetime(data['trade_date'])
        return data.sort_values(by='trade_date').reset_index(drop=True).set_index('trade_date')

    @classmethod
    def hkshsz(cls, result):
        data = cls._split(result, 'hkshsz_info')
        if data.empty:
            return data
        data['trade_date'] = pd.to_datetime(data['trade_date'])
        return data.sort_values(by='trade_date').reset_index(drop=True).set_index('trade_date')
    
    
    @classmethod
    def theme_info(cls, result):
        data = cls._split(result, 'theme_info')
        data['update_time'] = pd.to_datetime(data['update_time'])
        return data.sort_values(by='update_time',ascending=False).reset_index(drop=True)
    
        
class Event():
    @classmethod
    def _split(cls, result, name):
        columns = result[name]['columns']
        items = result[name]['items']
        data = pd.DataFrame.from_dict(items, orient='columns')
        data.columns=columns
        return data
    
    @classmethod
    def _record(cls, result, name):
        data = pd.DataFrame.from_dict(result[name])
        return data
    
    @classmethod
    def event_members(cls, result):
        return pd.DataFrame(result['members'])[
            ['tid','trade_date','title','update_time','sentiment','returns','event']]
    
    @classmethod
    def basic(cls, result):
        return pd.DataFrame.from_dict([result['basic_info']])
    
    @classmethod
    def timeline(cls, result):
        data = cls._record(result, 'timeline')
        data['start_time'] = pd.to_datetime(data['start_time'])
        data['end_time'] = pd.to_datetime(data['end_time'])
        return data.sort_values(by='start_time').reset_index(drop=True)
    
    @classmethod
    def thmem_benchmark(cls, result):
        data = result['returns']
        alpha_res = []
        for d in data:
            alpha_res.append({'tid':d['tid'],'name':d['name'],'returns':d['benchmark']})
        return pd.DataFrame(alpha_res)
    
    @classmethod
    def theme_cumreturns(cls, result):
        data = result['returns']
        alpha_res = []
        for d in data:
            df = cls._split(d,'combine')
            df['name'] = d['name']
            df['tid'] = d['tid']
            alpha_res.append(df)
        returns = pd.concat(alpha_res)
        return returns.set_index(['tid','name']).groupby(
            level=['tid','name']).apply(lambda x: np.exp(x[['returns']].sum()) - 1).reset_index()
            
        
class Detail():
    @classmethod
    def _split(cls, result, name):
        columns = result[name]['columns']
        items = result[name]['items']
        data = pd.DataFrame.from_dict(items, orient='columns')
        data.columns=columns
        return data
    
    @classmethod
    def _record(cls, result, name):
        data = pd.DataFrame.from_dict(result[name])
        return data
    
    @classmethod
    def basic(cls, result):
        return pd.DataFrame.from_dict([result['basic_info']])
        
    @classmethod
    def indicators(cls,result):
        data = cls._split(result, 'indicators_info')
        data['trade_date'] = pd.to_datetime(data['trade_date'])
        return data.sort_values(by='trade_date').reset_index(drop=True).set_index('trade_date')
    
    @classmethod
    def sentiment(cls, result):
        data = cls._split(result, 'sentiment_info')
        data['trade_date'] = pd.to_datetime(data['trade_date'])
        return data.sort_values(by='trade_date').reset_index(drop=True).set_index('trade_date')
    
    @classmethod
    def hkshsz(cls, result):
        data = cls._split(result, 'hzshsz_info')
        data['trade_date'] = pd.to_datetime(data['trade_date'])
        return data.sort_values(by='trade_date').reset_index(drop=True).set_index('trade_date')
    
    
    @classmethod
    def flowmoney(cls, result):
        data = cls._split(result, 'flowmoney_info')
        data['trade_date'] = pd.to_datetime(data['trade_date'])
        return data.sort_values(by='trade_date').reset_index(drop=True).set_index('trade_date')
        
        
    @classmethod
    def returns(cls, result):
        def to(returns):
            returns['trade_date'] = pd.to_datetime(returns['trade_date'])
            return returns.sort_values(by='trade_date').reset_index(drop=True)
        returns = result['returns_info']
        returns1m = to(cls._split(returns, '-21b')).set_index('trade_date')
        returns1w = to(cls._split(returns, '-5b')).set_index('trade_date')
        returns1q = to(cls._split(returns, '-63b')).set_index('trade_date')
        returnsc = to(to(cls._split(returns, 'con'))).set_index('trade_date')
        return {'1m':returns1m,'1w':returns1w,'1q':returns1q,
               'con':returnsc}
        
        
        #return data.sort_values(by='trade_date').reset_index(drop=True)

    @classmethod
    def members(cls,result):
        data = cls._split(result, 'members_info')
        return data
        
    @classmethod
    def news(cls, result):
        data = cls._record(result, 'news_info')
        if data.empty:
            return data
        data['publish_time'] = pd.to_datetime(data['publish_time'])
        return data.sort_values(by='publish_time').reset_index(drop=True)
    
    @classmethod
    def selstock(cls, result):
        data = cls._record(result, 'selstock_info')
        data['trade_date'] = pd.to_datetime(data['trade_date'])
        return data.sort_values(by='trade_date').reset_index(drop=True)
    
    @classmethod
    def sentistock(cls, result):
        data = cls._record(result, 'sentistock_info')
        data['trade_date'] = pd.to_datetime(data['trade_date'])
        return data.sort_values(by='trade_date').reset_index(drop=True)
    
    
        
    