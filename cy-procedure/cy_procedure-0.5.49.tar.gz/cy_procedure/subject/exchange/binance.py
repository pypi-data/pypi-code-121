import math
import time
import traceback
import pandas as pd
import numpy as np
from datetime import datetime
from cy_components.utils.functions import *
from cy_components.helpers.formatter import *
from cy_widgets.exchange.provider import *
from cy_widgets.trader.exchange_trader import *

# 订单状态对照表
binance_order_state = {
    'EXPIRED': '过期',
    'REJECTED': '被拒绝',
    'CANCELED': '撤单成功',
    'NEW': '等待成交',
    'PARTIALLY_FILLED': '部分成交',
    'FILLED': '完全成交',
}


class BinanceHandler:

    short_sleep_time = 1
    medium_sleep_time = 2

    def __init__(self, ccxt_provider: CCXTProvider):
        self.__ccxt_provider = ccxt_provider
        self.__lending_products = None
        self.__fee_percent = 0  # 订单里已经把手续费扣掉返回了，不需要计算
        self.__price_precision_info = None
        self.__min_qty_info = None

    def fetch_all_lending_product(self):
        """所有活期产品"""

        # https://binance-docs.github.io/apidocs/spot/cn/#baa37cb2f9
        # [{
        #    "asset": "BTC",
        #    "avgAnnualInterestRate": "0.00250025",
        #    "canPurchase": true,
        #    "canRedeem": true,
        #    "dailyInterestPerThousand": "0.00685000",
        #    "featured": true,
        #    "minPurchaseAmount": "0.01000000",
        #    "productId": "BTC001",
        #    "purchasedAmount": "16.32467016",
        #    "status": "PURCHASING",
        #    "upLimit": "200.00000000",
        #    "upLimitPerUser": "5.00000000"
        # }, {...}]
        self.__lending_products = self.__ccxt_provider.ccxt_object_for_query.sapi_get_lending_daily_product_list()
        return self.__lending_products

    def daily_lending_product(self, coin_name):
        """查找对应币种的活期产品"""
        if self.__lending_products is None:
            self.fetch_all_lending_product()
        filtered = list(filter(lambda x: x['asset'].lower() == coin_name.lower(), self.__lending_products))
        return filtered[0] if filtered else None

    def purchase_daily_lending_product(self, product_id, amount):
        """购买活期"""
        return self.__ccxt_provider.ccxt_object_for_query.sapi_post_lending_daily_purchase({
            "productId": product_id,
            "amount": amount,
            "timestamp": int(datetime.now().timestamp() * 1000)
        })

    def redeem_daily_lending_product(self, product_id, amount):
        """赎回活期"""
        return self.__ccxt_provider.ccxt_object_for_query.sapi_post_lending_daily_redeem({
            "productId": product_id,
            "amount": amount,
            "timestamp": int(datetime.now().timestamp() * 1000),
            'type': 'FAST'
        })

    def fetch_daily_lending_holding(self, asset):
        """查询活期持仓"""
        return self.__ccxt_provider.ccxt_object_for_query.sapi_get_lending_daily_token_position({
            "asset": asset,
            "timestamp": int(datetime.now().timestamp() * 1000)
        })

    def lending_interest_history(self, begin_time, end_time, asset):
        """查询活期利息"""
        parameters = {
            "lendingType": "DAILY",
            "startTime": begin_time,
            "endTime": end_time,
            "asset": asset,
            "size": 100,
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        return self.__ccxt_provider.ccxt_object_for_query.sapiGetLendingUnionInterestHistory(parameters)

    def all_premium(self, parameters={}):
        """所有合约溢价信息"""
        return self.__ccxt_provider.ccxt_object_for_query.dapiPublicGetPremiumIndex(parameters)

    def fetch_balance(self, type="spot"):
        """查询余额
        type: spot/margin/future"""
        return self.__ccxt_provider.ccxt_object_for_query.fetch_balance({'type': type})

    def transfer_margin(self, coin_name, amount, type=1):
        """全仓杠杆账户划转

        Parameters
        ----------
        type : int, optional
            1: in, 2: out
        """
        return self.__ccxt_provider.ccxt_object_for_query.sapi_post_margin_transfer({
            'asset': coin_name,
            'amount': amount,
            'type': type
        })

    def handle_spot_buying(self, coin_pair, amount, trader_logger):
        """现货买入"""
        order = Order(coin_pair, amount, 0)  # Only set base coin amount
        executor = ExchangeOrderExecutorFactory.executor(self.__ccxt_provider, order, trader_logger)
        # 下单
        response = executor.handle_long_order_request()
        if response is None:
            raise ConnectionError("Request buying order failed")
        # Binance 手续费已经扣掉了
        # {'id': '701037299',
        # 'clientOrderId': 'Se8IFlpHyWpsY7OaYkhKC1',
        # 'timestamp': 1597589153872,
        # 'datetime': '2020-08-16T14:45:53.872Z',
        # 'lastTradeTimestamp': None,
        # 'symbol': 'BNB/USDT',
        # 'type': 'limit',
        # 'side': 'buy',
        # 'price': 23.3236,
        # 'amount': 0.47,
        # 'cost': 10.854319,
        # 'average': 23.094295744680853,
        # 'filled': 0.47,
        # 'remaining': 0.0,
        # 'status': 'closed',
        # 'fee': None,
        # 'trades': None}
        price = response['average']
        cost = response['cost']
        filled = response['filled']
        buy_amount = math.floor(filled * (1 - self.__fee_percent) * 1e8) / 1e8  # *1e8 向下取整再 / 1e8
        return {
            'price': price,
            'cost': cost,
            'amount': buy_amount
        }

    def handle_spot_selling(self, coin_pair, amount, trader_logger):
        """现货卖出"""
        order = Order(coin_pair, 0, amount, side=OrderSide.SELL)  # Only set trade coin amount
        executor = ExchangeOrderExecutorFactory.executor(self.__ccxt_provider, order, trader_logger)
        # place order
        response = executor.handle_close_order_request()
        if response is None:
            raise ConnectionError("Request selling order failed")
        price = response['average']
        cost = response['cost']
        filled = response['filled']
        return {
            'price': price,
            'cost': cost,
            'amount': filled
        }

    def fetch_order_placing_cfg_if_needed(self):
        """获取下单精度相关参数"""
        if self.__min_qty_info is None or self.__price_precision_info is None:
            for i in range(10):
                try:
                    exchange_info = self.__ccxt_provider.ccxt_object_for_query.fapiPublic_get_exchangeinfo()
                    # symbol_list = [x['symbol'] for x in exchange_info['symbols']]  # 获取所有可交易币种的list

                    # 从exchange_info中获取每个币种最小交易量
                    self.__min_qty_info = {x['symbol']: int(math.log(float(x['filters'][1]['minQty']), 0.1)) for x in exchange_info['symbols']}
                    # 案例：{'BTCUSDT': 3, 'ETHUSDT': 3, 'BCHUSDT': 3, 'XRPUSDT': 1, 'EOSUSDT': 1, 'LTCUSDT': 3, 'TRXUSDT': 0}

                    # 从exchange_info中获取每个币种下单精度
                    self.__price_precision_info = {x['symbol']: int(math.log(float(x['filters'][0]['tickSize']), 0.1)) for x in exchange_info['symbols']}
                    break
                except Exception as _:
                    if i >= 4:
                        raise ValueError('fetch_order_placing_cfg_if_needed failed.')
                    time.sleep(self.short_sleep_time)

    def all_usdt_swap_symbols(self):
        """ 永续USDT币对 """
        cps = list(self.__ccxt_provider.ccxt_object_for_fetching.load_markets().keys())
        cps = list(filter(lambda x: '/USDT' in x, cps))
        return cps

    def fetch_binance_swap_equity(self):
        """
        获取币安永续合约账户的当前净值
        """
        # 获取当前账户净值
        balance = self.__ccxt_provider.ccxt_object_for_query.fapiPrivate_get_balance()  # 获取账户净值
        balance = pd.DataFrame(balance)
        equity = float(balance[balance['asset'] == 'USDT']['balance'])
        return equity

    def fetch_binance_ticker_data(self):
        """
        # 获取币安的ticker数据
        使用ccxt的接口fapiPublic_get_ticker_24hr()获取ticker数据
                        priceChange  priceChangePercent  weightedAvgPrice     lastPrice    lastQty  ...      openTime     closeTime      firstId       lastId      count
        symbol                                                                                 ...
        BTCUSDT     377.720000               3.517      10964.340000  11118.710000      0.039  ...  1.595927e+12  1.596013e+12  169966030.0  171208339.0  1242251.0
        ETHUSDT       9.840000               3.131        316.970000    324.140000      4.380  ...  1.595927e+12  1.596013e+12   72997450.0   73586755.0   589302.0
        ...
        XLMUSDT       0.002720               2.838          0.096520      0.098570    203.000  ...  1.595927e+12  1.596013e+12   12193167.0   12314848.0   121682.0
        ADAUSDT       0.002610               1.863          0.143840      0.142680   1056.000  ...  1.595927e+12  1.596013e+12   17919791.0   18260724.0   340914.0
        XMRUSDT       2.420000               3.013         81.780000     82.740000      0.797  ...  1.595927e+12  1.596013e+12    4974234.0    5029877.0    55644.0
        :param binance:
        :return:
        """
        tickers = self.__ccxt_provider.ccxt_object_for_query.fapiPublic_get_ticker_24hr()
        tickers = pd.DataFrame(tickers, dtype=float)
        tickers.set_index('symbol', inplace=True)

        return tickers['lastPrice']

    def place_order(self, symbol_info, symbol_last_price):
        """ 中性策略成批下单 """
        self.fetch_order_placing_cfg_if_needed()
        for symbol, row in symbol_info.dropna(subset=['实际下单量']).iterrows():
            # 计算下单量：按照最小下单量向下取整
            quantity = row['实际下单量']
            quantity = float(f'{quantity:.{self.__min_qty_info[symbol]}f}')

            # 检测是否需要开启只减仓
            reduce_only = np.isnan(row['目标下单份数']) or row['目标下单份数'] * quantity < 0
            quantity = abs(quantity)  # 下单量取正数

            if quantity == 0:
                print(symbol, quantity, '实际下单量为0，不下单')
                continue

            # 计算下单方向、价格
            if row['实际下单量'] > 0:
                side = 'BUY'
                price = symbol_last_price[symbol] * 1.02
            else:
                side = 'SELL'
                price = symbol_last_price[symbol] * 0.98

            # 对下单价格这种最小下单精度
            price = float(f'{price:.{self.__price_precision_info[symbol]}f}')

            if (quantity * price) < 5 and not reduce_only:
                print(symbol, quantity, '实际下单量小于5u，不下单')
                continue

            # 下单参数
            params = {'symbol': symbol, 'side': side, 'type': 'LIMIT', 'price': price, 'quantity': quantity,
                      'clientOrderId': str(time.time()), 'timeInForce': 'GTC', 'reduceOnly': reduce_only}
            # 下单
            print('下单参数：', params)
            try:
                open_order, _ = retry_wrapper(self.__ccxt_provider.ccxt_object_for_order.fapiPrivate_post_order, params, sleep_seconds=5)
                print('下单完成，下单信息：', open_order, '\n')
            except Exception as e:
                print('下单失败', str(e))

    def cal_order_price(self, price, order_type, ratio=0.02):
        """ 为了达到成交的目的，计算实际委托价格会向上或者向下浮动一定比例默认为0.02 """
        if order_type in [1, 4]:
            return price * (1 + ratio)
        elif order_type in [2, 3]:
            return price * (1 - ratio)

    def binance_future_place_order(self, coin_pair_str, symbol_signals, signal_price, holding, equity_balance, leverage, max_try_amount=5):
        """
        # 在合约市场下单
        :param symbol_info:
        :param symbol_config:
        :param symbol_signal:
        :param max_try_amount:
        :return:
        """
        self.fetch_order_placing_cfg_if_needed()
        order_id_list = []
        # 按照交易信号下单
        for order_type in symbol_signals:
            for i in range(max_try_amount):
                try:
                    # 当只要开仓或者平仓时，直接下单操作即可。但当本周期即需要平仓，又需要开仓时，需要在平完仓之后，
                    # 重新评估下账户资金，然后根据账户资金计算开仓账户然后开仓。下面这行代码即处理这个情形。
                    # "长度为2的判定"定位【平空，开多】或【平多，开空】两种情形，"下单类型判定"定位 处于开仓的情形。
                    if len(symbol_signals) == 2 and order_type in [1, 2]:  # 当两个条件同时满足时，说明当前处于平仓后，需要再开仓的阶段。
                        time.sleep(self.short_sleep_time)  # 短暂的休息1s，防止之平仓后，账户没有更新
                        equity_balance = self.fetch_binance_swap_equity()

                    reduce_only = False
                    # 平仓，就是开反向的量
                    if order_type in [3, 4]:
                        quantity = holding
                        reduce_only = True
                    else:
                        quantity = equity_balance * leverage / signal_price

                    quantity = float(f'{quantity:.{self.__min_qty_info[coin_pair_str]}f}')
                    # 检测是否需要开启只减仓
                    quantity = abs(quantity)  # 下单量取正数

                    if quantity == 0:
                        raise ValueError(f'{coin_pair_str} {quantity} 实际下单量为0，不下单')

                    # 计算下单方向、价格
                    price = self.cal_order_price(signal_price, order_type)
                    if order_type in [1, 4]:  # 开多、平空
                        side = 'BUY'
                    else:
                        side = 'SELL'

                    # 对下单价格这种最小下单精度
                    price = float(f'{price:.{self.__price_precision_info[coin_pair_str]}f}')

                    if (quantity * price) < 5 and not reduce_only:
                        raise ValueError(f'{coin_pair_str} {quantity} 实际下单量小于5u，不下单')

                    # 下单参数
                    params = {'symbol': coin_pair_str, 'side': side, 'type': 'LIMIT', 'price': price, 'quantity': quantity,
                              'clientOrderId': str(time.time()), 'timeInForce': 'GTC', 'reduceOnly': reduce_only}
                    # 下单
                    print('下单参数：', params)
                    open_order, _ = retry_wrapper(self.__ccxt_provider.ccxt_object_for_order.fapiPrivate_post_order, params, sleep_seconds=5)
                    print('下单完成，下单信息：', open_order, '\n')
                    order_id_list.append(open_order['orderId'])
                    break
                except Exception as e:
                    print(traceback.format_exc())
                    print(coin_pair_str, '下单失败，稍等后继续尝试')
                    time.sleep(self.short_sleep_time)
                    if i == (max_try_amount - 1):
                        print('下单失败次数超过max_try_amount，终止下单')
                        raise ValueError('下单失败次数超过max_try_amount')
        return order_id_list

    def update_future_order_info(self, coin_pair_str, order_ids, max_try_amount=5):
        """
        根据订单号，检查订单信息，获得相关数据
        :param exchange:
        :param symbol_config:
        :param symbol_order:
        :param max_try_amount:
        :return:

        函数返回值案例：
                                symbol      信号价格                       信号时间  订单状态 开仓方向 委托数量 成交数量    委托价格    成交均价                      委托时间
        4476028903965698  eth-usdt  227.1300 2020-03-01 11:53:00.580063  完全成交   开多  100  100  231.67  227.29  2020-03-01T03:53:00.896Z
        4476028904156161  xrp-usdt    0.2365 2020-03-01 11:53:00.580558  完全成交   开空  100  100  0.2317  0.2363  2020-03-01T03:53:00.906Z
        """

        all_order_infos = dict()
        # 这个遍历下单id
        for order_id in order_ids:
            time.sleep(self.medium_sleep_time)  # 每次获取下单数据时sleep一段时间
            order_info = None
            # 根据下单id获取数据
            for i in range(max_try_amount):
                try:
                    para = {
                        'symbol': coin_pair_str,
                        'orderId': order_id,
                        'timestamp': DateFormatter.convert_local_date_to_timestamp(datetime.now())
                    }
                    order_info = self.__ccxt_provider.ccxt_object_for_query.fapiPrivate_get_order(para)
                    break
                except Exception as e:
                    print(e)
                    print('根据订单号获取订单信息失败，稍后重试')
                    time.sleep(self.medium_sleep_time)
                    if i == max_try_amount - 1:
                        raise ValueError('重试次数过多，获取订单信息失败，程序退出')

            if order_info:
                def format_order_type(order_info):
                    if order_info['side'] == 'BUY':
                        return '平空' if order_info['reduceOnly'] else '开多'
                    else:
                        return '平多' if order_info['reduceOnly'] else '开空'

                info_dict = {
                    "订单状态": binance_order_state[order_info["status"]],
                    "开仓方向": format_order_type(order_info),
                    "委托数量": order_info["origQty"],
                    "成交数量": order_info["executedQty"],
                    "委托价格": order_info["price"],
                    "成交均价": order_info["avgPrice"],
                    "委托时间": DateFormatter.convert_timestamp_to_local_date(order_info["time"])
                }
                all_order_infos[order_id] = info_dict
            else:
                raise ValueError(f'根据订单号 {order_id} 获取订单信息失败次数超过max_try_amount')

        return all_order_infos

    def update_symbol_info(self, symbol_list, add_pos_infos=False):
        """
        # 获取币安账户的实际持仓
        使用ccxt接口：fapiPrivate_get_positionrisk，获取账户持仓
        返回值案例
                    positionAmt  entryPrice  markPrice  unRealizedProfit  liquidationPrice  ...  maxNotionalValue  marginType isolatedMargin  isAutoAddMargin
        positionSide
        symbol                                                                            ...
        XMRUSDT         0.003    63.86333  63.877630          0.000043             0.000  ...            250000       cross            0.0            false         LONG
        ATOMUSDT       -0.030     2.61000   2.600252          0.000292           447.424  ...             25000       cross            0.0            false        SHORT
        :param exchange:
        :param symbol_list:
        :return:
        """
        # 获取原始数据
        position_risk = self.__ccxt_provider.ccxt_object_for_query.fapiPrivate_get_positionrisk()

        # 将原始数据转化为dataframe
        position_risk = pd.DataFrame(position_risk, dtype='float')

        # 整理数据
        position_risk.rename(columns={'positionAmt': '当前持仓量'}, inplace=True)
        position_risk = position_risk[position_risk['当前持仓量'] != 0]  # 只保留有仓位的币种
        position_risk.set_index('symbol', inplace=True)  # 将symbol设置为index

        # 创建symbol_info
        symbol_info = pd.DataFrame(index=symbol_list, columns=['当前持仓量'])
        symbol_info['当前持仓量'] = position_risk['当前持仓量']
        symbol_info['当前持仓量'].fillna(value=0, inplace=True)
        if add_pos_infos:
            # 持仓方向
            symbol_info.loc[symbol_info['当前持仓量'] > 0, '持仓方向'] = 1
            symbol_info.loc[symbol_info['当前持仓量'] < 0, '持仓方向'] = -1
            symbol_info['持仓方向'].fillna(value=0, inplace=True)
            # 权益
            symbol_info['持仓收益'] = position_risk['unRealizedProfit']
            symbol_info['持仓收益'].fillna(value=0, inplace=True)
            # 价格
            symbol_info['持仓均价'] = position_risk['entryPrice']
            symbol_info['当前价格'] = position_risk['markPrice']
            # 账户权益
            symbol_info['账户权益'] = self.fetch_binance_swap_equity()

        return symbol_info

    # === 子账户相关 ===

    def all_sub_class_emails(self):
        """子账户邮箱列表"""
        return [x['email'] for x in self.__ccxt_provider.ccxt_object_for_query.wapiGetSubAccountList()['subAccounts']]
