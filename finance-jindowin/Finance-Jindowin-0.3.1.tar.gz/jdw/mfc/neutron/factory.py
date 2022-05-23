from jdw.kdutils.logger import kd_logger
from jdw.mfc.neutron.analysis import Analysis
from jdw.mfc.neutron.strategy import Strategy
from jdw.kdutils.data.mongodb import MongoDBManager
from jdw.mfc import NTN_COLL,NTN_URL
import pandas as pd
import os,pdb,zlib,json,itertools

class Factory(object):
    def __init__(self):
        self._analysis = Analysis()
        self._strategy = Strategy()
        self._mongo_client = MongoDBManager(uri=NTN_URL)

    def _fetch_mongo(self, **kwargs):
        columns = None if 'columns' not in kwargs else kwargs['columns']
        if columns is not None:
            results = self._mongo_client[NTN_COLL][kwargs['name']].find(
                kwargs['query'],dict(zip(columns, [1 for i in range(0,len(columns))]))
                )
        else:
            results = self._mongo_client[NTN_COLL][kwargs['name']].find(
                kwargs['query'])
        results = pd.DataFrame(results)
        results = results.drop(['_id'],axis=1) if not results.empty else pd.DataFrame(columns=columns)
        return results


    def attillio(self, **kwargs):
        return self._analysis.attillio(**kwargs)
    
    def vanous(self, **kwargs):
        return self._analysis.vanous(**kwargs)

    def butz(self, **kwargs):
        return self._analysis.butz(**kwargs)

    def slonim(self, **kwargs):
        return self._analysis.slonim(**kwargs)

    def neelam(self, **kwargs):
        return self._analysis.neelam(**kwargs)
    
    def glick(self, **kwargs):
        return self._strategy.glick(**kwargs)
    
    def jaque(self, **kwargs):
        return self._strategy.jaque(**kwargs)

    def results(self, **kwargs):
        def neelam(results):
            def transfer(result):
                data = {}
                rt = json.loads(zlib.decompress(result['content']))
                signal = pd.DataFrame.from_dict(rt['signal']['items'],
                                                orient='columns')
                if signal.empty:
                    signal = pd.DataFrame(columns=rt['signal']['columns'])
                signal.columns=rt['signal']['columns']

                returns = pd.DataFrame.from_dict(rt['returns']['items'],
                            orient='columns')
                if returns.empty:
                    returns = pd.DataFrame(columns=rt['returns']['columns'])
                returns.columns=rt['returns']['columns']
                data['signal'] = signal
                data['returns'] = returns
                data['params'] = rt['params']
                data['target'] = rt['target']
                return data
            data = [transfer(rt) for rt in results.to_dict(orient='records')]
            return data

        def glick(results):
            def transfer(result):
                rt = json.loads(zlib.decompress(result['content']))
                columns = rt['columns']
                items = rt['items']
                data = pd.DataFrame.from_dict(items, orient='columns')
                if data.empty:
                    return pd.DataFrame(columns=columns)
                data.columns=columns
                return data
            results = [transfer(rt) for rt in results.to_dict(orient='records')]
            return pd.concat(results,axis=0)

        def vanous(results):
            def transfer(result):
                rt = json.loads(zlib.decompress(result['content']))
                columns = rt['columns']
                items = rt['items']
                data = pd.DataFrame.from_dict(items, orient='columns')
                if data.empty:
                    return pd.DataFrame(columns=columns)
                data.columns=columns
                return data.set_index(['trade_date','code'])
            results = [transfer(rt) for rt in results.to_dict(orient='records')]
            return pd.concat(results,axis=1)

        def attillio(results):
            def transfer1(result):
                pos = pd.DataFrame.from_dict(result['postion']['items'],
                                                orient='columns')
                if pos.empty:
                    return pd.DataFrame(columns=result['postion']['columns'])
                pos.columns=result['postion']['columns']

                returns = pd.DataFrame.from_dict(result['returns']['items'],
                            orient='columns')
                if returns.empty:
                    return pd.DataFrame(columns=result['returns']['columns'])
                returns.columns=result['returns']['columns']

                result['postion'] = pos
                result['returns'] = returns
                return result

            def transfer(result):
                rts = json.loads(zlib.decompress(result['content']))
                rts = [transfer1(rt) for rt in rts]
                return rts
            results = [transfer(rt) for rt in results.to_dict(orient='records')]
            results = list(itertools.chain.from_iterable(results))
            return results

        query = {'task_id':kwargs['task_id']}
        name = kwargs['name'] + '_task_detail'
        ###查询进度
        columns = ['task_id','session_id','progress','remarks']
        process = self._fetch_mongo(query=query, name=name, columns=columns)
        if process.empty:
            return
        ##检测
        process = process.to_dict(orient='records')
        results = [ps for ps in process if ps['progress'] < 100]
        if len(results) > 0:
            _ = [kd_logger.info("task_id:{0} session:{1} progress:{2}, remark:{3}".format(
                    r['task_id'], r['session_id'], r['progress'], r['remarks'])) for r in results]
            return
        ### 返回结果
        results = self._fetch_mongo(query=query, name=name)
        if results.empty:
            return 
        ### 解析结果
        if kwargs['name'] == 'vanous':
            results = vanous(results).reset_index()
        elif kwargs['name'] == 'butz':
            results = vanous(results).reset_index()
        elif kwargs['name'] == 'slonim':
            results = attillio(results)
        elif kwargs['name'] == 'attillio':
            results = attillio(results)
        elif kwargs['name'] == 'glick':
            results = glick(results)
        elif kwargs['name'] == 'jaque':
            results = glick(results)
        elif kwargs['name'] == 'neelam':
            results = neelam(results)
        return results
