import abc
from prometheus.base import protocol


class callback(metaclass=abc.ABCMeta):
    """策略的回调对象的抽象基类"""

    def __init__(self):
        """初始化"""
        pass

    def get_insert_template(self) -> dict:
        """获取报单模板"""
        return protocol.ctp.insert_order_template()

    def get_cancel_template(self) -> dict:
        """获取撤单模板"""
        return protocol.ctp.cancel_order_template()
    
    @abc.abstractmethod
    def register_strategy(self, strategy_id: str, strategy, setting_path: str):
        """注册策略"""
        pass
    
    @abc.abstractmethod
    def subscribe(self, strategy_id: str, exchange_id: str, instrument_id: str):
        """订阅任务入队列"""
        pass
    
    @abc.abstractmethod
    def unsubscribe(self, strategy_id: str, exchange_id: str, instrument_id: str):
        """退订任务入队列"""
        pass
    
    @abc.abstractmethod
    def insert_order(self, strategy_id: str, order: dict):
        """报单任务入队列"""
        pass
    
    @abc.abstractmethod
    def cancel_order(self, strategy_id: str, order: dict):
        """撤单任务入队列"""
        pass
    
    @abc.abstractmethod
    def query_instrument(self, strategy_id: str, exchange_id: str, instrument_id: str):
        """查询标的任务入队列"""
        pass
    
    @abc.abstractmethod
    def query_account(self, strategy_id: str):
        """查询账户任务入队列"""
        pass
    
    @abc.abstractmethod
    def query_position(self, strategy_id: str):
        """查询持仓任务入队列"""
        pass
    
    @abc.abstractmethod
    def stop_strategy(self, strategy_id: str):
        """停止指定策略"""
        pass
    
    @abc.abstractmethod
    def run(self):
        pass

