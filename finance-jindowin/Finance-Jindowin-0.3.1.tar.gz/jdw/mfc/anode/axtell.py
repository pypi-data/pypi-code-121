import sys,importlib,traceback,pdb
from pathlib import Path
from datetime import datetime
from threading import Thread
import pandas as pd

from vnpy.event import Event, EventEngine
from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.trader.constant import Direction, Offset, OrderType, Interval
from vnpy.trader.object import (OrderRequest,HistoryRequest,SubscribeRequest,LogData)
from vnpy.trader.datafeed import BaseDatafeed, get_datafeed

### 通用引擎
class Axtell(BaseEngine):
    setting_filename  = "script_trader_setting.json"

    def __init__(self, main_engine, event_engine, name='axtell'):
        super().__init__(main_engine, event_engine, name)
        self._event_log  = "AxtellLog"
        self._name = name
        self.strategy_active = False
        self.strategy_thread = None

    def init(self) -> None:
        """启动策略引擎"""
        if True:
            self.write_log("数据服务初始化成功")

    def start_strategy(self, script_path):
        """运行策略线程中的策略方法"""
        if self.strategy_active:
            return
        self.strategy_active = True

        self.strategy_thread = Thread(
            target=self.run_strategy, args=(script_path,))
        self.strategy_thread.start()

        self.write_log("策略交易脚本启动")

    def run_strategy(self, script_path) -> None:
        """加载策略脚本并调用run函数"""
        path = Path(script_path)
        sys.path.append(str(path.parent))

        script_name = path.parts[-1]
        module_name = script_name.replace(".py", "")

        try:
            module = importlib.import_module(module_name)
            importlib.reload(module)
            module.run(self)
        except Exception:
            msg: str = f"触发异常已停止\n{traceback.format_exc()}"
            self.write_log(msg)

    def stop_strategy(self) -> None:
        """停止运行中的策略"""
        if not self.strategy_active:
            return
        self.strategy_active = False

        if self.strategy_thread:
            self.strategy_thread.join()
        self.strategy_thread = None

        self.write_log("策略交易脚本停止")

    def connect_gateway(self, setting, gateway_name) -> None:
        self.main_engine.connect(setting, gateway_name)

    def contract(self, vt_symbol):
        return self.main_engine.get_contract(vt_symbol)

    def send_order(self,vt_symbol, price, volume, direction,
            offset ,order_type):
        contract  = self.get_contract(vt_symbol)
        if not contract:
            return 
        req = OrderRequest(symbol=contract.symbol, exchange=contract.exchange,
                            direction=direction, type=order_type, volume=volume,
                            price=price, offset=offset, reference=self._name)

        vt_orderid: str = self.main_engine.send_order(req, contract.gateway_name)
        return vt_orderid

    def subscribe(self, symbols):
        contracts = self.get_all_contracts(use_df=True)
        contracts = contracts.set_index('symbol').loc[symbols].reset_index()[['symbol','exchange','gateway_name']]
        for  contract in contracts.itertuples():
            if contract:
                req: SubscribeRequest = SubscribeRequest(
                    symbol=contract.symbol,
                    exchange=contract.exchange
                )
                self.main_engine.subscribe(req, contract.gateway_name)

    def buy(self, vt_symbol, price, volume: float, order_type=OrderType.LIMIT) -> str:
        return self.send_order(vt_symbol, price, volume, Direction.LONG, Offset.OPEN, order_type)

    def sell(self,vt_symbol, price,volume, order_type = OrderType.LIMIT):
        return self.send_order(vt_symbol, price, volume, Direction.SHORT, Offset.CLOSE, order_type)

    def short(self, vt_symbol, price, volume, order_type = OrderType.LIMIT):
        """"""
        return self.send_order(vt_symbol, price, volume, Direction.SHORT, Offset.OPEN, order_type)

    def cover(self, vt_symbol, price, volume, order_type = OrderType.LIMIT):
        """"""
        return self.send_order(vt_symbol, price, volume, Direction.LONG, Offset.CLOSE, order_type)

    def cancel_order(self, vt_orderid):
        """"""
        order = self.get_order(vt_orderid)
        if not order:
            return
        req = order.create_cancel_request()
        self.main_engine.cancel_order(req, order.gateway_name)

    def get_tick(self, vt_symbol, use_df = False):
        """"""
        return get_data(self.main_engine.get_tick, arg=vt_symbol, use_df=use_df)

    def get_ticks(self, vt_symbols, use_df = False):
        """"""
        ticks = []
        for vt_symbol in vt_symbols:
            tick = self.main_engine.get_tick(vt_symbol)
            ticks.append(tick)
        if not use_df:
            return ticks
        else:
            return to_df(ticks)

    def get_order(self, vt_orderid, use_df = False):
        """"""
        return get_data(self.main_engine.get_order, arg=vt_orderid, use_df=use_df)

    def get_orders(self, vt_orderids, use_df):
        """"""
        orders = []
        for vt_orderid in vt_orderids:
            order = self.main_engine.get_order(vt_orderid)
            orders.append(order)

        if not use_df:
            return orders
        else:
            return to_df(orders)

    def get_trades(self, vt_orderid, use_df = False):
        """"""
        trades: list = []
        all_trades = self.main_engine.get_all_trades()

        for trade in all_trades:
            if trade.vt_orderid == vt_orderid:
                trades.append(trade)

        if not use_df:
            return trades
        else:
            return to_df(trades)

    def get_all_active_orders(self, use_df = False):
        """"""
        return get_data(self.main_engine.get_all_active_orders, use_df=use_df)

    def get_contract(self, vt_symbol, use_df = False):
        """"""
        return get_data(self.main_engine.get_contract, arg=vt_symbol, use_df=use_df)

    def get_all_contracts(self, use_df = False):
        """"""
        return get_data(self.main_engine.get_all_contracts, use_df=use_df)

    def get_account(self, vt_accountid, use_df = False):
        """"""
        return get_data(self.main_engine.get_account, arg=vt_accountid, use_df=use_df)

    def get_all_accounts(self, use_df = False):
        """"""
        return get_data(self.main_engine.get_all_accounts, use_df=use_df)

    def get_position(self, vt_positionid, use_df = False):
        """"""
        return get_data(self.main_engine.get_position, arg=vt_positionid, use_df=use_df)

    def get_all_positions(self, use_df = False):
        """"""
        return get_data(self.main_engine.get_all_positions, use_df=use_df)

    def get_bars(self, vt_symbol, start_date, interval, use_df = False):
        """"""
        contract = self.main_engine.get_contract(vt_symbol)
        if not contract:
            return []

        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.now()

        req = HistoryRequest(symbol=contract.symbol, exchange=contract.exchange,
            start=start, end=end, interval=interval)

        return get_data(self.datafeed.query_bar_history, arg=req, use_df=use_df)

    def write_log(self, msg):
        """"""
        log = LogData(msg=msg, gateway_name=self._name)
        print(f"{log.time}\t{log.msg}")

        event: Event = Event(self._event_log, log)
        self.event_engine.put(event)

    def send_email(self, msg):
        """"""
        subject: str = "脚本策略引擎通知"
        self.main_engine.send_email(subject, msg)


def to_df(data_list):
    """"""
    if not data_list:
        return None

    dict_list = [data.__dict__ for data in data_list]
    return pd.DataFrame(dict_list)


def get_data(func, arg = None, use_df = False):
    """"""
    if not arg:
        data = func()
    else:
        data = func(arg)

    if not use_df:
        return data
    elif data is None:
        return data
    else:
        if not isinstance(data, list):
            data = [data]
        return to_df(data)