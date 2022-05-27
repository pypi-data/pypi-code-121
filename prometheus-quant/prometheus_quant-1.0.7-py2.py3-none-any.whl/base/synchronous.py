# 本类封装所有对zmq的操作，以及获取所有的消息模板，获取所有的说明文档，
# 构成基础api，供上层的普罗米修斯系统调用，也可为希望高度定制的用户直接调用

import zmq
import json
import time
from prometheus.base import protocol


class api:
    """封装系统基本api"""

    def __init__(self, setting_path: str, identity: str):
        """初始化"""

        # 尝试获取配置信息
        self._setting = self.__get_setting(setting_path)
        assert self._setting is not None, "配置文件错误"

        # 启动zmq下上文
        self._context = zmq.Context()

        # 行情部分的
        self._requester = self._context.socket(zmq.REQ)
        self._requester.connect(self._setting[identity]["subscribe_url"])

        self._listener = self._context.socket(zmq.SUB)
        self._listener.connect(self._setting[identity]["listen_url"])
        
        # 设置过滤条件
        # self._listener.subscribe("")
        self._listener.setsockopt(zmq.SUBSCRIBE, "".encode('utf-8'))

    def __get_setting(self, setting_path: str) -> dict:
        """读取传入的配置文件路径"""
        if not setting_path.endswith(".json"):
            return None
        with open(setting_path, 'r', encoding='utf8') as json_file:
            return json.load(json_file)

    def send(self, message: dict):
        """发送消息"""
        # 将消息字典转为json字符串，再转换为ByteArray
        message_byte_array = json.dumps(message).encode('utf-8')
        # 发送消息
        self._requester.send(message_byte_array)

    def receive(self) -> dict:
        """接受数据"""
        # 监听应答
        message_byte_array = self._requester.recv()
        # 将buffer转换为字符串，再转换为字典
        return json.loads(message_byte_array.decode('utf-8'))

    def listen(self) -> dict:
        # 监听推送
        message_byte_array = self._listener.recv()
        # 将buffer转换为字符串，再转换为字典
        return json.loads(message_byte_array.decode('utf-8'))


class market_data(api):
    """行情通信api封装"""

    def __init__(self, setting_path: str):
        """初始化"""
        # 调用父类初始化方法
        super(market_data, self).__init__(setting_path, "market_data")

    def subscribe(self, strategy_id: str, exchange_id: str, instrument_id: str) -> bool:
        """订阅行情"""
        # 创建消息的字典格式，发送消息
        self.send(protocol.ctp.subscribe_quote_request(strategy_id, exchange_id, instrument_id))

        # 监听返回的订阅应答
        return self.receive().get("MessageStatus", False)

    def unsubscribe(self, strategy_id: str, exchange_id: str, instrument_id: str) -> bool:
        """退订行情"""
        # 创建消息的字典格式，发送消息
        self.send(protocol.ctp.unsubscribe_quote_request(strategy_id, exchange_id, instrument_id))

        # 监听返回的退订应答
        return self.receive().get("MessageStatus", False)

    def listen_quote(self) -> dict:
        """监听行情"""
        return self.listen().get("Quote", dict())


class trader(api):
    """交易通信api封装"""

    def __init__(self, setting_path: str):
        """初始化"""
        # 调用父类初始化方法
        super(trader, self).__init__(setting_path, "trade")

    def insert_order(self, strategy_id: str, order: dict) -> (bool, str):
        """保单"""
        # 报单引用不可超过12个字符
        if 12 < len(order["OrderRef"]):
            return False, "报单引用OrderRef不可超过13个字符"

        # 创建消息的字典格式，发送消息
        self.send(protocol.ctp.insert_order_request(strategy_id, order))

        # 监听返回的订阅应答
        response = self.receive()
        return response.get("MessageStatus", False), response.get("FailureReason", None)

    def cancel_order(self, strategy_id: str, order: dict) -> (bool, str):
        """退订行情"""
        # 报单引用不可超过12个字符
        if 12 < len(order["OrderRef"]):
            return False, "报单引用OrderRef不可超过13个字符"

        # 创建消息的字典格式，发送消息
        self.send(protocol.ctp.cancel_order_request(strategy_id, order))

        # 监听返回的退订应答
        response = self.receive()
        return response.get("MessageStatus", False), response.get("FailureReason", None)

    def query_instrument(self, strategy_id: str, exchange_id: str, instrument_id: str) -> bool:
        """查询标的"""
        # 创建消息的字典格式，发送消息
        self.send(protocol.ctp.query_instrument_request(strategy_id, exchange_id, instrument_id))

        # 监听返回的订阅应答
        return self.receive().get("MessageStatus", False)

    def query_account(self, strategy_id: str) -> bool:
        """查询账户"""
        # 创建消息的字典格式，发送消息
        self.send(protocol.ctp.query_account_request(strategy_id))

        # 监听返回的订阅应答
        return self.receive().get("MessageStatus", False)

    def query_position(self, strategy_id: str) -> bool:
        """查询持仓"""
        # 创建消息的字典格式，发送消息
        self.send(protocol.ctp.query_position_request(strategy_id))

        # 监听返回的订阅应答
        return self.receive().get("MessageStatus", False)

    def listen_publish(self) -> (str, str, dict):
        """监听交易回报或查询回报"""
        publish = self.listen()
        if "Order" in publish:
            return "Order", publish.get("StrategyID"), publish.get("Order") 
        elif "Query" in publish:
            return "Query", publish.get("StrategyID"), publish.get("Query") 
        else:
            return "", publish.get("StrategyID"), dict()

