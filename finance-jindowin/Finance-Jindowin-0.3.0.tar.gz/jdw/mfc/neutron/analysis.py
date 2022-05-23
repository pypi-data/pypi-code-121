from nameko.standalone.rpc import ClusterRpcProxy
from jdw.utils import split_list, create_task_id
from jdw.mfc import MQ_URL,NTN_COLL
import pandas as pd
import itertools,os,pdb

class Analysis(object):
    def attillio(self, **kwargs):
        windows = split_list(kwargs['windows'],1)
        columns = split_list(kwargs['columns'],4)
        weekdays = split_list(kwargs['weekdays'],2)
        binses = split_list(kwargs['binses'],2)
        task_id = create_task_id(kwargs)
        config = {'AMQP_URI': MQ_URL}
        with ClusterRpcProxy(config) as rpc:
            for param in itertools.product(windows, columns, weekdays, binses):
                session_id = create_task_id(param)
                rpc.realtime_servicer.factor_attillio.call_async(
                    codes=kwargs['codes'], begin_date=kwargs['begin_date'], 
                end_date=kwargs['end_date'], columns=param[1], 
                windows=param[0], weekdays=param[2], 
                binses=param[3], retain=kwargs['retain'], 
                task_id=task_id, session=session_id)
        return task_id

    def vanous(self, **kwargs):
        columns = split_list(list(kwargs['columns'].values()),1)
        methods = split_list(kwargs['methods'],3)
        task_id = create_task_id(kwargs)
        config = {'AMQP_URI': MQ_URL}
        with ClusterRpcProxy(config) as rpc:
            for param in itertools.product(columns, methods):
                category = list(kwargs['columns'].keys())[list(kwargs['columns'].values()).index(param[0][0])]
                session_id = create_task_id(param)
                rpc.realtime_servicer.factor_vanous.call_async(category=category, codes=kwargs['codes'], 
                    begin_date=kwargs['begin_date'], end_date=kwargs['end_date'], 
                    columns=param[0][0], methods=param[1], 
                    task_id=task_id, session=session_id)
        return task_id

    def butz(self, **kwargs):
        columns = split_list(list(kwargs['columns'].values()),1)
        methods = split_list(kwargs['methods'],3)
        task_id = create_task_id(kwargs)
        config = {'AMQP_URI': MQ_URL}
        with ClusterRpcProxy(config) as rpc:
            for param in itertools.product(columns, methods):
                category = list(kwargs['columns'].keys())[list(kwargs['columns'].values()).index(param[0][0])]
                session_id = create_task_id(param)
                rpc.realtime_servicer.factor_butz.call_async(category, codes=kwargs['codes'], begin_date=kwargs['begin_date'], 
                    end_date=kwargs['end_date'], factors=param[0][0], methods=param[1], 
                    task_id=task_id, session=session_id)
        return task_id

    def neelam(self, **kwargs):
        factors = split_list(kwargs['factors'],1)
        methods = split_list(kwargs['methods'],1)
        task_id = create_task_id(kwargs)
        config = {'AMQP_URI': MQ_URL}
        with ClusterRpcProxy(config) as rpc:
            for param in itertools.product(factors, methods):
                session_id = create_task_id(param)
                rpc.realtime_servicer.factor_neelam.call_async(
                    codes=kwargs['codes'], begin_date=kwargs['begin_date'],
                    end_date=kwargs['end_date'], factors=param[0][0], 
                    method=param[1][0],task_id=task_id,
                    session=session_id)
        return  task_id


    def slonim(self, mongo_client, **kwargs):
        def fetch_parent(task_id, name='vanous_task_detail'):
            columns = ['task_id','session_id']
            query = {'task_id':kwargs['task_id']}
            results = mongo_client[NTN_COLL][name].find(
                query, dict(zip(columns, [1 for i in range(0,len(columns))])))
            results = pd.DataFrame(results)
            results = results.drop(['_id'],axis=1) if not results.empty else pd.DataFrame(
                columns=columns)
            return results

        results = fetch_parent(kwargs['task_id'], name='vanous_task_detail')
        results =  results if not results.empty else fetch_parent(
            kwargs['task_id'], name='butz_task_detail')

        session_ids = results['session_id'].unique().tolist()
        session = split_list(session_ids, 1)
        windows = split_list(kwargs['windows'],1)
        weekdays = split_list(kwargs['weekdays'],2)
        binses = split_list(kwargs['binses'],2)
        task_id = create_task_id(kwargs)
        config = {'AMQP_URI': MQ_URL}
        with ClusterRpcProxy(config) as rpc:
            for param in itertools.product(windows, session, weekdays, binses):
                session_id = create_task_id(param)
                rpc.realtime_servicer.factor_slonim.call_async(
                    src_task=kwargs['task_id'], src_session=param[1][0], 
                    windows=param[0], weekdays=param[2], 
                    binses=param[3], retain=kwargs['retain'], 
                    task_id=task_id, session=session_id)
        return task_id