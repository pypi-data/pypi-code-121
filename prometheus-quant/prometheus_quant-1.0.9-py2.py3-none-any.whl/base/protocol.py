import json
from datetime import datetime


class ctp:
    """封装协议,创建所有的请求消息"""

    @classmethod
    def subscribe_quote_request(cls, strategy_id: str, exchange_id: str, instrument_id: str) -> dict:
        """创建行情订阅请求"""
        return {
            "MessageType": "Request",
            "MessageTopic": "Quote",
            "MessageOperate": "Subscribe",
            "StrategyID": strategy_id,
            "Quote": {
                "ExchangeID": exchange_id,
                "InstrumentID": instrument_id,
            }
        }

    @classmethod
    def unsubscribe_quote_request(cls, strategy_id: str, exchange_id: str, instrument_id: str) -> dict:
        """创建行情退订请求"""
        return {
            "MessageType": "Request",
            "MessageTopic": "Quote",
            "MessageOperate": "Unsubscribe",
            "StrategyID": strategy_id,
            "Quote": {
                "ExchangeID": exchange_id,
                "InstrumentID": instrument_id,
            }
        }

    @classmethod
    def insert_order_request(cls, strategy_id: str, order: dict) -> dict:
        """创建报单请求"""
        return {
            "MessageType": "Request",
            "MessageTopic": "Order",
            "MessageOperate": "Insert",
            "StrategyID": strategy_id,
            "Order": order
        }

    @classmethod
    def cancel_order_request(cls, strategy_id: str, order: dict) -> dict:
        """创建撤单请求"""
        return {
            "MessageType": "Request",
            "MessageTopic": "Order",
            "MessageOperate": "Cancel",
            "StrategyID": strategy_id,
            "Order": order
        }

    @classmethod
    def query_instrument_request(cls, strategy_id: str, exchange_id: str, instrument_id: str) -> dict:
        """创建查询标的请求"""
        return {
            "MessageType": "Request",
            "MessageTopic": "Query",
            "StrategyID": strategy_id,
            "Query": {
                "QueryItem": "Instrument",
                "ExchangeID": exchange_id,
                "InstrumentID": instrument_id,
            }
        }

    @classmethod
    def query_account_request(cls, strategy_id: str) -> dict:
        """创建查询账户请求"""
        return {
            "MessageType": "Request",
            "MessageTopic": "Query",
            "StrategyID": strategy_id,
            "Query": {
                "QueryItem": "TradingAccount",
            }
        }

    @classmethod
    def query_position_request(cls, strategy_id: str) -> dict:
        """创建查询持仓请求"""
        return {
            "MessageType": "Request",
            "MessageTopic": "Query",
            "StrategyID": strategy_id,
            "Query": {
                "QueryItem": "InvestorPosition",
            }
        }
    
    @classmethod
    def insert_order_template(self) -> dict:
        """获取一个报单模板"""
        return {
            "ExchangeID": "SHFE",
            "InstrumentID": "au2208",
            "OrderRef": "user-au2208",
            "OrderPriceType": "Limit",
            "Direction": "Buy",
            "CombOffsetFlag": "Open",
            "CombHedgeFlag": "Speculation",
            "LimitPrice": 390,
            "VolumeTotalOriginal": 10,
            "TimeCondition": "GFD",
            "GTDDate": datetime.now().strftime("%Y%m%d"),
            "VolumeCondition": "AV",
            "MinVolume": 1,
            "ContingentCondition": "Immediately",
            "ForceCloseReason": "NotForceClose",
            "IsAutoSuspend": 0,
            "UserForceClose": 0
        }

    @classmethod
    def cancel_order_template(self) -> dict:
        """获取一个撤单模板"""
        return {
            "ExchangeID": "SHFE",
            "InstrumentID": "au2208",
            "OrderRef": "user-au2208",
            "ActionFlag": "Delete",
            "VolumeChange": 10
        }

