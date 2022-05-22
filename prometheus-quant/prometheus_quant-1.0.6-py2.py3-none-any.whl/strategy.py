import os
import sys
import abc
import json
import asyncio
import logging
from time import sleep
from prometheus.base import protocol
from prometheus.callback import callback
from multiprocessing import Process, Queue, cpu_count
from prometheus.base.asynchronous import market_data, trader


class template(metaclass=abc.ABCMeta):
    """策略基类模板"""

    def __init__(self):
        """初始化"""
        self.__strategy_id = None         # 策略ID，策略的唯一（由用户向studio注册策略时赋予，并由studio管理）
        self.__callback = None            # 所归属的studio（studio在实例化策略的时候，自动传入）
        self.__subscription_list = []     # 订阅列表
        self.__logger = None

    @property
    def strategy_id(self):
        """策略id"""
        return self.__strategy_id

    @strategy_id.setter
    def strategy_id(self, strategy_id: str):
        """策略id"""
        # 设置策略id
        self.__strategy_id = strategy_id

        # 设置日志
        handler = logging.FileHandler(f"{strategy_id}.log", 'a', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.__logger = logging.getLogger(strategy_id)
        self.__logger.setLevel(logging.DEBUG)
        self.__logger.addHandler(handler)

    @property
    def callback(self):
        """回调对象"""
        return self.__callback

    @callback.setter
    def callback(self, callback_objective: callback):
        """回调对象"""
        self.__callback = callback_objective

    @property
    def subscription_list(self):
        """订阅列表"""
        return self.__subscription_list

    @subscription_list.setter
    def subscription_list(self, subscription_list: list):
        """订阅列表"""
        self.__subscription_list = subscription_list

    def get_insert_template(self) -> dict:
        """获取报单模板"""
        return self.__callback.get_insert_template()

    def get_cancel_template(self) -> dict:
        """获取撤单模板"""
        return self.__callback.get_cancel_template()

    def subscribe(self, exchange_id: str, instrument_id: str):
        """订阅"""
        if self.__callback is None:
            return
        self.__callback.subscribe(
            self.__strategy_id, exchange_id, instrument_id
        )

    def unsubscribe(self, exchange_id: str, instrument_id: str):
        """退订"""
        if self.__callback is None:
            return
        self.__callback.unsubscribe(
            self.__strategy_id, exchange_id, instrument_id
        )

    def insert_order(self, order: dict):
        """报单"""
        if self.__callback is None:
            return

        # 报单引用不可超过12个字符
        if 12 < len(order["OrderRef"]):
            return False, "报单引用OrderRef不可超过13个字符"

        self.__callback.insert_order(
            self.__strategy_id, order
        )

    def cancel_order(self, order: dict):
        """撤单"""
        if self.__callback is None:
            return
            
        # 报单引用不可超过12个字符
        if 12 < len(order["OrderRef"]):
            return False, "报单引用OrderRef不可超过13个字符"

        self.__callback.cancel_order(
            self.__strategy_id, order
        )

    def query_instrument(self, exchange_id: str, instrument_id: str):
        """查询标的"""
        if self.__callback is None:
            return
        self.__callback.query_instrument(
            self.__strategy_id, exchange_id, instrument_id
        )

    def query_account(self):
        """查询账户"""
        if self.__callback is None:
            return
        self.__callback.query_account(self.__strategy_id)

    def query_position(self):
        """查询持仓"""
        if self.__callback is None:
            return
        self.__callback.query_position(self.__strategy_id)

    def stop(self):
        """停止策略"""
        if self.__callback is None:
            return
        self.__callback.stop_strategy(self.__strategy_id)

    def log_debug(self, content: str):
        """日志 - 调试信息"""
        self.__logger.debug(content)

    def log_info(self, content: str):
        """日志 - 普通信息"""
        self.__logger.info(content)

    def log_warning(self, content: str):
        """日志 - 警告信息"""
        self.__logger.warning(content)

    def log_error(self, content: str):
        """日志 - 错误信息"""
        self.__logger.error(content)

    def log_critical(self, content: str):
        """日志 - 灾难信息"""
        self.__logger.critical(content)

    @abc.abstractmethod
    def on_init(self, setting: dict):
        """初始化回调"""
        pass

    @abc.abstractmethod
    def on_start(self):
        """策略启动回调"""
        pass

    @abc.abstractmethod
    def on_stop(self):
        """策略停止回调"""
        pass

    @abc.abstractmethod
    def on_subscribe(self, exchange_id: str, instrument_id: str, success: bool):
        """订阅应答回调"""
        pass

    @abc.abstractmethod
    def on_unsubscribe(self, exchange_id: str, instrument_id: str, success: bool):
        """退订应答回调"""
        pass

    @abc.abstractmethod
    def on_tick(self, tick: dict):
        """行情推送回调"""
        pass

    @abc.abstractmethod
    def on_insert(self, order: dict, success: bool, failure_reason: str):
        """报单应答回调"""
        pass

    @abc.abstractmethod
    def on_cancel(self, order: dict, success: bool, failure_reason: str):
        """撤单应答回调"""
        pass

    @abc.abstractmethod
    def on_order(self, order: dict):
        """订单回报回调"""
        pass

    @abc.abstractmethod
    def on_query(self, query: dict, success: bool):
        """查询应答回调"""
        pass

    @abc.abstractmethod
    def on_report(self, query: dict):
        """查询回报回调"""
        pass


class group_manager(callback):
    """量化交易实验室"""

    def __init__(self, log_name: str):
        """初始化"""
        # 调用父类初始化方法
        super(group_manager, self).__init__()

        # 日志设定
        handler = logging.FileHandler(f"{log_name}.log", 'a', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.__logger = logging.getLogger(log_name)
        self.__logger.setLevel(logging.DEBUG)
        self.__logger.addHandler(handler)

        self.__to_manager_queue = None
        self.__to_study_queue = None

        self.__strategy_registration_table = dict()      # 策略实例化记录{策略ID: 策略元对象}
        self.__setting_registration_table = dict()       # 策略配置文件记录{策略ID: 策略配置}

        self.__subscription_registration_table = dict()  # 策略订阅登记表{标的ID: set(策略ID)}

    def register_strategy(self, strategy_id: str, strategy: template, setting_path: str):
        """注册策略"""

        # 断言每次传入的策略名称是唯一的，不然报错，保证实例化之后的策略可被管理
        assert strategy_id not in self.__strategy_registration_table or strategy_id not in self.__setting_registration_table, f"{strategy_id}已存在记录中"

        # 登记所有的策略
        self.__strategy_registration_table[strategy_id] = strategy
        
        # 记录所有的配置
        with open(setting_path, 'r', encoding='utf8') as setting_file:
            self.__setting_registration_table[strategy_id] = json.load(setting_file) 

    def subscribe(self, strategy_id: str, exchange_id: str, instrument_id: str):
        """订阅任务入队列"""
        if self.__to_study_queue is None:
            return
        self.log_info(f"策略{strategy_id}, 订阅{exchange_id}-{instrument_id}")
        self.__to_study_queue.put(
            protocol.ctp.subscribe_quote_request(
                strategy_id, exchange_id, instrument_id
            )
        )

    def unsubscribe(self, strategy_id: str, exchange_id: str, instrument_id: str):
        """退订任务入队列"""
        if self.__to_study_queue is None:
            return
        self.log_info(f"策略{strategy_id}, 退订{exchange_id}-{instrument_id}")
        self.__to_study_queue.put(
            protocol.ctp.unsubscribe_quote_request(
                strategy_id, exchange_id, instrument_id
            )
        )

    def insert_order(self, strategy_id: str, order: dict):
        """报单任务入队列"""
        if self.__to_study_queue is None:
            return
        self.log_info(f"策略{strategy_id}, 报单{order}")
        self.__to_study_queue.put(
            protocol.ctp.insert_order_request(
                strategy_id, order
            )
        )

    def cancel_order(self, strategy_id: str, order: dict):
        """撤单任务入队列"""
        if self.__to_study_queue is None:
            return
        self.log_info(f"策略{strategy_id}, 撤单{order}")
        self.__to_study_queue.put(
            protocol.ctp.cancel_order_request(
                strategy_id, order
            )
        )

    def query_instrument(self, strategy_id: str, exchange_id: str, instrument_id: str):
        """查询标的任务入队列"""
        if self.__to_study_queue is None:
            return
        self.log_info(f"策略{strategy_id}, 查询标的{exchange_id}-{instrument_id}")
        self.__to_study_queue.put(
            protocol.ctp.query_instrument_request(
                strategy_id, exchange_id, instrument_id
            )
        )

    def query_account(self, strategy_id: str):
        """查询账户任务入队列"""
        if self.__to_study_queue is None:
            return
        self.log_info(f"策略{strategy_id}, 查询账户")
        self.__to_study_queue.put(
            protocol.ctp.query_account_request(strategy_id)
        )

    def query_position(self, strategy_id: str):
        """查询持仓任务入队列"""
        if self.__to_study_queue is None:
            return
        self.log_info(f"策略{strategy_id}, 查询持仓")
        self.__to_study_queue.put(
            protocol.ctp.query_position_request(strategy_id)
        )

    def stop_strategy(self, strategy_id: str):
        """停止指定策略"""
        self.log_info(f"策略{strategy_id}, 请求停止")

        # 判断该策略是否被登记
        if strategy_id not in self.__strategy_registration_table:
            return
        strategy = self.__strategy_registration_table[strategy_id]

        # 删除所有记录
        for instrument_id in self.__subscription_registration_table:
            self.__subscription_registration_table[instrument_id].discard(strategy_id)
        del self.__strategy_registration_table[strategy_id]
        del self.__setting_registration_table[strategy_id]

        # 回调该策略停止回调
        strategy.on_stop()

        self.log_info(f"策略{strategy_id}, 停止成功")

    def log_debug(self, content: str):
        """日志 - 调试信息"""
        self.__logger.debug(content)

    def log_info(self, content: str):
        """日志 - 普通信息"""
        self.__logger.info(content)

    def log_warning(self, content: str):
        """日志 - 警告信息"""
        self.__logger.warning(content)

    def log_error(self, content: str):
        """日志 - 错误信息"""
        self.__logger.error(content)

    def log_critical(self, content: str):
        """日志 - 灾难信息"""
        self.__logger.critical(content)

    def run(self, to_manager_queue: Queue, to_study_queue: Queue):
        """启动studio"""
        # 记录队列
        self.__to_manager_queue = to_manager_queue
        self.__to_study_queue = to_study_queue

        # 准备好所有的数据容器
        self.__init_all_table()

        # 为所有的策略自动执行订阅
        self.__init_subscribe()
        
        # 初始化所有的策略，调用on_init和on_start
        self.__init_all_strategies()
        
        # 进入事件循环
        self.__event_dispatch()

    def __init_all_table(self):
        """初始化所有的策略"""
        # 为所有的策略自身添加策略id，并注册回调
        for strategy_id in self.__strategy_registration_table:
            # 为每一个策略添加id
            self.__strategy_registration_table[strategy_id].strategy_id = strategy_id
            # 为每一个策略注册回调
            self.__strategy_registration_table[strategy_id].callback = self

    def __init_subscribe(self):
        """初始化所有的订阅，依据用户在策略中设置的订阅列表，自动执行订阅"""
        self.log_info(f"系统启动执行自动化订阅")
        # 遍历每个策略的订阅列表
        for strategy_id in self.__strategy_registration_table:
            # 遍历订阅列表中的每一个标的id
            for exchange_id, instrument_id in self.__strategy_registration_table[strategy_id].subscription_list:
                # 执行订阅
                self.subscribe(strategy_id, exchange_id, instrument_id)
                
    def __init_all_strategies(self):
        """初始化所有的策略"""
        # 实例化所有的策略
        for strategy_id in self.__strategy_registration_table:
            # 初始化每一个策略
            self.log_info(f"策略{strategy_id}, 初始化")
            self.__strategy_registration_table[strategy_id].on_init(self.__setting_registration_table[strategy_id])
            # 触发每个策略启动
            self.log_info(f"策略{strategy_id}, 启动")
            self.__strategy_registration_table[strategy_id].on_start()

    def __event_dispatch(self):
        """事件循环，不断监听消息进程消息队列发来的消息，并做处理"""
        while True:
            # 如果没有策略登记，退出循环
            if 0 == len(self.__strategy_registration_table):
                break

            # 监听队列
            if self.__to_manager_queue is None or self.__to_manager_queue.empty():
                continue

            # 从队列中提取消息
            message = self.__to_manager_queue.get()

            # 处理消息
            try:
                self.__message_handler(message)
            except Exception as e:
                self.log_error(f"远端通信消息处理失败, 消息: {message}，执行丢弃处理")

    def __message_handler(self, message):
        """处理消息"""
        # 获取消息类型/主题
        type = message.get("MessageType", None)
        topic = message.get("MessageTopic", None)

        # 如果类型不是应答，或推送，退出
        if type not in ["Response", "Publish"] or type is None or topic is None:
            self.log_error(f"收到非法消息, {message}，消息丢弃处理")
            return

        if "Quote" == topic:
            self.__quote_message_handler(message)
        elif "Order" == topic:
            self.__order_message_handler(message)
        elif "Query" == topic:
            self.__query_message_handler(message)
        else:
            self.log_error(f"消息主题非法, {message}，消息丢弃处理")

    def __quote_message_handler(self, message):
        """处理行情消息"""
        # 解析
        type, quote = message["MessageType"], message["Quote"]
        exchange_id, instrument_id = quote["ExchangeID"], quote["InstrumentID"]

        # 分类处理
        if "Response" == type:
            strategy_id, success = message["StrategyID"], message["MessageStatus"]

            # 回调策略
            self.__strategy_registration_table[strategy_id].on_subscribe(
                exchange_id=exchange_id, 
                instrument_id=instrument_id,
                success=success
            )

            # 登记订阅注册表
            operate = message["MessageOperate"]
            if success and "Subscribe" == operate:
                if instrument_id not in self.__subscription_registration_table:
                    self.__subscription_registration_table[instrument_id] = set()
                self.__subscription_registration_table[instrument_id].add(strategy_id)
            elif success and "Unsubscribe" == operate:
                if instrument_id in self.__subscription_registration_table:
                    self.__subscription_registration_table[instrument_id].discard(strategy_id)
            else:
                return

        elif "Publish" == type:
            # 查询订阅该标的的所有策略, 并推送行情
            for strategy_id in self.__subscription_registration_table[instrument_id]:
                self.__strategy_registration_table[strategy_id].on_tick(quote)

        else:
            return

    def __order_message_handler(self, message):
        """处理交易消息"""
        # 解析
        type, strategy_id, order = message["MessageType"], message["StrategyID"], message["Order"]

        # 分类处理
        if "Response" == type:
            success = message["MessageStatus"]
            operate = message["MessageOperate"]
            failure_reason = "" if success else message["FailureReason"]
            if "Insert" == operate:
                # 回调策略
                self.__strategy_registration_table[strategy_id].on_insert(
                    order=order,
                    success=success, 
                    failure_reason=failure_reason
                )
            elif "Cancel" == operate:
                # 回调策略
                self.__strategy_registration_table[strategy_id].on_cancel(
                    order=order,
                    success=success, 
                    failure_reason=failure_reason
                )
            else:
                return
        elif "Publish" == type:
            self.__strategy_registration_table[strategy_id].on_order(order)
        else:
            return

    def __query_message_handler(self, message):
        """处理查询消息"""
        # 解析
        type, strategy_id, operate, query = message["MessageType"], message["StrategyID"], message["MessageOperate"], message["Query"]

        # 分类处理
        if "Response" == type:
            success = message["MessageStatus"]
            # 回调策略
            self.__strategy_registration_table[strategy_id].on_query(
                query=query, 
                success=success
            )
        elif "Publish" == type:
            self.__strategy_registration_table[strategy_id].on_report(query)
        else:
            return


class studio:
    """量化交易实验室"""

    def __init__(self, setting_path: str, processes_count: int, log_name: str = None):
        """初始化方法"""
        # 日志设定
        if not log_name:
            log_name = f"study{os.getpid()}"
        handler = logging.FileHandler(f"{log_name}.log", 'a', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.__logger = logging.getLogger(log_name)
        self.__logger.setLevel(logging.DEBUG)
        self.__logger.addHandler(handler)

        # 创建通信器
        self.__market_data = market_data(setting_path)   # 行情api类
        self.__trader = trader(setting_path)             # 交易api类

        # 创建进程池
        assert processes_count > 0, "最大进程数设置错误"
        self.__pool = {}

        # 按进程数量创建策略组管理器表{子进程编号: 策略管理组（子进程）}
        self.__group_manager_table = {}
        for index in range(processes_count):
            self.__group_manager_table[index] = group_manager(f"{log_name}_subprocess_{index}")

        # 创建各个进程的消息队列{子进程编号: 队列}
        self.__to_manager_queue_table = {}
        self.__to_study_queue_table = {}
        for index in range(processes_count):
            self.__to_manager_queue_table[index] = Queue()
            self.__to_study_queue_table[index] = Queue()

        # 创建策略映射表{策略id: 子进程编号}， 注册策略的时候，填装数据
        self.__strategy_process_mapping = {}

        # 创建策略订阅记录{标的id: set(子进程编号)}
        self.__manager_registration_table = {}

    def register_strategy(self, process_index: int, strategy_id: str, strategy: template, setting_path: str):
        """注册进程"""
        # 判断用户传入的进程编号是否合理
        assert 0 <= process_index < len(self.__group_manager_table), f"不存在id编号为{process_index}的进程"
        
        # 将策略注册到各个策略管理组
        self.__group_manager_table[process_index].register_strategy(
            strategy_id, strategy, setting_path
        )
        self.log_info(f"注册策略: {strategy_id}, 使用策略类: {type(strategy).__name__}, 配置文件: {setting_path}, 策略被注册于进程: {process_index}")

        # 记录策略所在进程
        self.__strategy_process_mapping[strategy_id] = process_index

    def log_debug(self, content: str):
        """日志 - 调试信息"""
        self.__logger.debug(content)

    def log_info(self, content: str):
        """日志 - 普通信息"""
        self.__logger.info(content)

    def log_warning(self, content: str):
        """日志 - 警告信息"""
        self.__logger.warning(content)

    def log_error(self, content: str):
        """日志 - 错误信息"""
        self.__logger.error(content)

    def log_critical(self, content: str):
        """日志 - 灾难信息"""
        self.__logger.critical(content)

    def run(self):
        """启动运行将所有策略管理组以子进程方式运行，监听zmq，并通过进程间队列传递消息"""
        # 启动所有的策略管理组子进程，并传入队列
        for index in self.__group_manager_table:
            process = Process(
                target=self.__group_manager_table[index].run, 
                args=(self.__to_manager_queue_table[index], self.__to_study_queue_table[index])
            )
            process.start()
            self.__pool[index] = (process)
            self.log_info(f"启动进程index={index}")

        # 监听zmq消息
        self.__event_dispatch()

        # 等待所有子进程结束
        for process in self.__pool:
            self.__pool[index].join()

    def __event_dispatch(self):
        """
            事件循环，三个个协程，
            1. 监控子进程是否运行
            2. 监听行情服务的publish
            3. 监听交易服务的publish
            4. 监听进程通信队列
        """
        self.log_info(f"启动事件循环")

        loop = None
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            loop = asyncio.get_event_loop_policy().new_event_loop()
        else:
            loop = asyncio.get_event_loop()

        loop.run_until_complete(asyncio.wait([
            self.__manager_monitor(),
            self.__quote_monitor(),
            self.__trade_monitor(),
            self.__message_monitor(),
        ]))

        loop.close()

    async def __manager_monitor(self):
        """监控所有的子进程是否还在运行，系统自动结束退出的关键机制"""
        while True:
            # 如果系统中没有子进程了，即没有策略在运行，退出
            if 0 == len(self.__group_manager_table):
                break

            # 检车所有进程是否存活着
            for index in list(self.__pool.keys()):
                # 如果记录的进程已经死亡，删除记录
                if not self.__pool[index].is_alive():
                    del self.__pool[index]
                    del self.__group_manager_table[index]
                    self.log_warning(f"检测进程{index}已停止")

            # 检查异步休息，将主进程的控制权交出来，供其他协程运行
            await asyncio.sleep(1)

    async def __quote_monitor(self):
        """监听行情信息"""
        while True:
            # 如果系统中没有子进程了，即没有策略在运行，退出
            if 0 == len(self.__group_manager_table):
                break

            # 监听行情
            publish = await self.__market_data.listen()
            quote = publish["Quote"]
            instrument_id = quote["InstrumentID"]
            # 查询订阅该标的的所有策略, 并推送行情
            if instrument_id in self.__manager_registration_table:
                for index in self.__manager_registration_table[instrument_id]:
                    self.__to_manager_queue_table[index].put(publish)

    async def __trade_monitor(self):
        """监听交易信息"""
        while True:
            # 如果系统中没有子进程了，即没有策略在运行，退出
            if 0 == len(self.__group_manager_table):
                break

            # 监听交易或查询回报
            publish = await self.__trader.listen()
            # 找到消息对应的队列，并将消息发送
            strategy_id = publish.get("StrategyID")
            index = self.__strategy_process_mapping[strategy_id]
            self.__to_manager_queue_table[index].put(publish)

    async def __message_monitor(self):
        """监听进程间通信队列"""
        while True:
            # 如果系统中没有子进程了，即没有策略在运行，退出
            if 0 == len(self.__group_manager_table):
                break

            # 遍历所有的进程间通信队列, 获取信息
            for index in self.__to_study_queue_table:
                # 队列为空，查询下一个队列
                if self.__to_study_queue_table[index].empty():
                    continue

                # 提取消息
                message = self.__to_study_queue_table[index].get()
                type = message.get('MessageType', None)
                topic = message.get('MessageTopic', None)
                if "Request" != type or type is None or topic is None:
                    self.log_error(f"收到子进程{index}发来的非法消息: {message}")
                    continue

                # 发送消息
                if "Quote" == topic:
                    # 发送订阅/退订任务
                    await self.__market_data.send(message)
                    response = await self.__market_data.receive()
                    # 返回应答
                    self.__to_manager_queue_table[index].put(response)
                    # 如果行情订阅/退订成功，记录/抹除记录
                    try:
                        status, operate, instrument_id = response["MessageStatus"], response["MessageOperate"], response["Quote"]["InstrumentID"]
                        if instrument_id not in self.__manager_registration_table:
                            self.__manager_registration_table[instrument_id] = set()
                        if status and "Subscribe" == operate: 
                            self.__manager_registration_table[instrument_id].add(index)
                        elif status and "Unsubscribe" == operate:
                            self.__manager_registration_table[instrument_id].discard(index)
                        else:
                            continue
                    except Exception as _:
                        self.log_error(f"行情订阅应答消息非法: {response}， 记录操作失败")

                elif "Order" == topic or "Query" == topic:
                    # 发送交易/查询任务
                    await self.__trader.send(message)
                    response = await self.__trader.receive()
                    # 返回应答
                    self.__to_manager_queue_table[index].put(response)
                else:
                    continue

            # 如果没有任务处理，防止本协程死循环，异步跳出让渡使用权
            await asyncio.sleep(0.01)
