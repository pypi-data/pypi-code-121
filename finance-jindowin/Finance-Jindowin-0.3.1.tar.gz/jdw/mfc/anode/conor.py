# -*- coding: utf-8 -*-
import importlib,pdb
import pandas as pd
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.event import EVENT_LOG,EVENT_TICK,EVENT_ORDER
from jdw.mfc.anode.axtell import Axtell

### 适配引擎
class Conor(object):
    def __init__(self, name='ctp'):
        self._name = name
        self._event_engine = EventEngine()
        self._event_engine.register(EVENT_LOG, self.process_log_event)
        self._event_engine.register(EVENT_TICK, self.process_tick)
        self._event_engine.register(EVENT_ORDER, self.process_order)
        self._main_engine = MainEngine(self._event_engine)
        module_name = "vnpy_{0}".format(self._name)
        self._market_data = {}
        try:
            module_class = importlib.import_module(module_name)
            getway_name = "{0}Gateway".format(self._name.capitalize())
            getway_module = module_class.__getattribute__(getway_name)
        except ImportError as e:
            raise(str(e))
            return
        self._main_engine.add_gateway(getway_module)
        self._trader_engine = self._main_engine.add_engine(Axtell)

    def process_log_event(self, event):
        log = event.data
        print(f"{log.time}\t{log.msg}")

    def process_order(self, event):
        print(event.data)

    def process_tick(self, event):
        self._market_data[event.data.symbol] = event.data

    def process_contract(self, event):
        print(event.data)

    def _create_config(self, **kwargs):
        config = {}
        config["用户名"] = kwargs['account_id']
        config["密码"] = kwargs['password']
        config["经纪商代码"] = kwargs['broker_id']
        config["交易服务器"] = kwargs['td_address']
        config["行情服务器"] = kwargs['md_address']
        config["产品名称"] = kwargs['app_id']
        config["授权编码"] = kwargs['auth_code']
        return config

    def start(self, **kwargs):
        config = self._create_config(**kwargs)
        self._trader_engine.connect_gateway(config, self._name.upper())

    def contract(self, symbol):
        self._trader_engine.contract(symbol)
        
    def subscribe(self, symbol):
        self._trader_engine.subscribe(symbol)

    def buy(self, symbol, price, volume): ###  开多仓
        return self._trader_engine.buy(symbol, price, volume)

    def sell(self, symbol, price, volume): ### 平多仓
        return self._trader_engine.sell(symbol, price, volume)
    
    def short(self, symbol, price, volume): ### 开空仓
        return self._trader_engine.short(symbol, price, volume)

    def cover(self, symbol, price, volume): ### 平空仓
        return self._trader_engine.cover(symbol, price, volume)
        
    def cancel_order(self, symbol, order_id):
        return self._trader_engine.cancel_order(symbol, order_id)

    def get_all_contracts(self, use_df=False):
        """"""
        return self._trader_engine.get_all_contracts(use_df)

    def get_account(self, vt_accountid: str, use_df: bool = False):
        """"""
        return self._trader_engine.get_account(vt_accountid, use_df)

    def get_all_accounts(self, use_df: bool = False):
        """"""
        return self._trader_engine.get_all_accounts(use_df=use_df)

    def get_all_positions(self, use_df: bool = False):
        """"""
        return self._trader_engine.get_all_positions(use_df=use_df)

    def get_tick(self, vt_symbol, use_df=False):
        return self._trader_engine.get_tick(vt_symbol=vt_symbol, use_df=use_df)

    def get_ticks(self, symbols, columns=None):
        cols = ['symbol','exchange','last_price',
                    'bid_price_1','ask_price_1'] if columns is None else columns
        market_data = pd.DataFrame(list(self._market_data.values()))
        market_data = market_data.set_index('symbol').loc[symbols].reset_index()
        return market_data[cols]
        #return self._trader_engine.get_ticks(vt_symbols=vt_symbols, use_df=use_df)