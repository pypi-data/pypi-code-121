import imp
from nameko.standalone.rpc import ClusterRpcProxy
from jdw.mfc import MQ_URL
from jdw.utils import split_list, create_task_id
import itertools,os

class Strategy(object):
    def glick(self, **kwargs):
        codes = split_list(kwargs['codes'],1)
        sel_session = split_list(kwargs['sel_session'],1)
        task_id = create_task_id(kwargs)
        config = {'AMQP_URI': MQ_URL}
        with ClusterRpcProxy(config) as rpc:
            for param in itertools.product(codes, sel_session):
                session_id = create_task_id(param)
                rpc.realtime_servicer.portfolio_glick.call_async(
                    sel_session=param[1], codes=param[0][0], 
                    begin_date=kwargs['begin_date'], 
                    end_date=kwargs['end_date'], name=kwargs['name'], 
                    task_id=task_id, session=session_id)
        return task_id

    def jaque(self, **kwargs):
        codes = split_list(kwargs['codes'], 1)
        sel_session = split_list(kwargs['sel_session'],1)
        parent = split_list(kwargs['parent'],1)
        task_id = create_task_id(kwargs)
        config = {'AMQP_URI': MQ_URL}
        with ClusterRpcProxy(config) as rpc:
            for param in itertools.product(codes, sel_session, parent):
                session_id = create_task_id(param)
                rpc.realtime_servicer.portfolio_jaque.call_async(
                    sel_session=param[1], parent=param[2],codes=param[0][0], 
                    begin_date=kwargs['begin_date'], 
                    end_date=kwargs['end_date'], name=kwargs['name'], 
                    task_id=task_id, session=session_id)