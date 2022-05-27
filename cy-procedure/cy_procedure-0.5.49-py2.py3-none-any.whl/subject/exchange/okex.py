import traceback
import math
import pandas as pd
from datetime import datetime
from cy_widgets.exchange.provider import *
from cy_widgets.trader.exchange_trader import *

# 订单对照表
okex_order_type = {
    '1': '开多',
    '2': '开空',
    '3': '平多',
    '4': '平空',
}

# 币种面值对照表
coin_value_table = {
    "btc-usdt": 0.01,
    "eos-usdt": 10,
    "eth-usdt": 0.1,
    "ltc-usdt": 1,
    "bch-usdt": 0.1,
    "xrp-usdt": 100,
    "etc-usdt": 10,
    "bsv-usdt": 1,
    "trx-usdt": 1000,
    'dot-usdt': 1,
    'link-usdt': 1,
}

# 订单状态对照表
okex_order_state = {
    '-2': '失败',
    '-1': '撤单成功',
    '0': '等待成交',
    '1': '部分成交',
    '2': '完全成交',
    '3': '下单中',
    '4': '撤单中',
}


class OKExHandler:

    short_sleep_time = 1
    medium_sleep_time = 2

    def __init__(self, ccxt_provider: CCXTProvider):
        self.__ccxt_provider = ccxt_provider
        self.__fee_percent = 0
        self.__all_swap_instruments = None

    def fetch_all_swap_instruments(self):
        """所有的永续合约"""
        self.__all_swap_instruments = self.__ccxt_provider.ccxt_object_for_fetching.swapGetInstruments()
        return self.__all_swap_instruments

    def fetch_all_delivery_instruments(self):
        """所有的交割合约"""
        return self.__ccxt_provider.ccxt_object_for_fetching.futuresGetInstruments()

    def fetch_swap_instrument_fund_rate(self, instrument_id):
        """获取合约费率"""
        return self.__ccxt_provider.ccxt_object_for_fetching.swapGetInstrumentsInstrumentIdFundingTime({
            "instrument_id": instrument_id
        })

    # ==== 账户相关 =====

    def fetch_future_account(self, max_try_amount=6):
        """
        ==== 通过ccxt、交易所接口获取合约账户信息
        :param exchange:
        :param max_try_amount:
        :return:

        本程序使用okex3中“交割合约API”、“所有币种合约账户信息”接口，获取合约账户所有币种的账户信息。
        使用ccxt函数：exchange.futures_get_accounts()  1次/10s
        请求此接口，okex服务器会在其数据库中遍历所有币对下的账户数据，有大量的性能消耗，请求频率较低，时间较长。

        接口返回数据格式样例：
        {'info':
        {
        'eth-usdt': {'auto_margin': '0', 'can_withdraw': '9.97342426', 'contracts': [{'available_qty': '9.97342426', 'fixed_balance': '0.02657574', 'instrument_id': 'ETH-USDT-200327', 'margin_for_unfilled': '0', 'margin_frozen': '0.027094', 'realized_pnl': '0.00051826', 'unrealized_pnl': '-0.0018'}], 'currency': 'USDT', 'equity': '9.99878826', 'liqui_mode': 'tier', 'margin_mode': 'fixed', 'total_avail_balance': '9.97342426'},
        'ltc-usdt': {'can_withdraw': '9.99970474', 'currency': 'USDT', 'equity': '9.99970474', 'liqui_fee_rate': '0.0005', 'liqui_mode': 'tier', 'maint_margin_ratio': '0.01', 'margin': '0', 'margin_for_unfilled': '0', 'margin_frozen': '0', 'margin_mode': 'crossed', 'margin_ratio': '10000', 'realized_pnl': '-0.00029526', 'total_avail_balance': '10', 'underlying': 'LTC-USDT', 'unrealized_pnl': '0'},
        'eos': {'can_withdraw': '6.49953151', 'currency': 'EOS', 'equity': '7.22172698', 'liqui_fee_rate': '0.0005', 'liqui_mode': 'tier', 'maint_margin_ratio': '0.01', 'margin': '0.72219547', 'margin_for_unfilled': '0', 'margin_frozen': '0.72219547', 'margin_mode': 'crossed', 'margin_ratio': '0.99996847', 'realized_pnl': '0', 'total_avail_balance': '7.29194531', 'underlying': 'EOS-USD', 'unrealized_pnl': '-0.07021833'},
        'eos-usdt': {'auto_margin': '0', 'can_withdraw': '9.91366074', 'contracts': [{'available_qty': '9.91366074', 'fixed_balance': '0.0827228', 'instrument_id': 'EOS-USDT-200327', 'margin_for_unfilled': '0', 'margin_frozen': '0.08167', 'realized_pnl': '-0.0010528', 'unrealized_pnl': '-0.0006'}], 'currency': 'USDT', 'equity': '9.99473074', 'liqui_mode': 'tier', 'margin_mode': 'fixed', 'total_avail_balance': '9.91366074'},
        返回结果说明：
        eth-usdt为usdt本位合约有持仓时返回的结果
        ltc-usdt为usdt本位合约没有持仓，但是账户有usdt时返回的结果
        eos-usdt为usdt本位合约同时有多、空持仓时返回的结果
        eos为币本位合约有持仓时返回的结果

        本函数输出示例：

            auto_margin can_withdraw                                          contracts currency       equity liqui_fee_rate liqui_mode maint_margin_ratio      margin margin_for_unfilled margin_frozen margin_mode margin_ratio realized_pnl total_avail_balance underlying unrealized_pnl
        eth-usdt           0   9.97342426  [{'available_qty': '9.97342426', 'fixed_balanc...     USDT   9.99847826            NaN       tier                NaN         NaN                 NaN           NaN       fixed          NaN          NaN          9.97342426        NaN            NaN
        ltc-usdt         NaN   9.99970474                                                NaN     USDT   9.99970474         0.0005       tier               0.01           0                   0             0     crossed        10000  -0.00029526                  10   LTC-USDT              0
        eos              NaN   6.49640362                                                NaN      EOS   7.21825155         0.0005       tier               0.01  0.72184793                   0    0.72184793     crossed   0.99996845            0          7.29194531    EOS-USD    -0.07369376
        eos-usdt           0   9.91366074  [{'available_qty': '9.91366074', 'fixed_balanc...     USDT   9.99473074            NaN       tier                NaN         NaN                 NaN           NaN       fixed          NaN          NaN          9.91366074        NaN            NaN
        btc-usdt         NaN  57.07262111                                                NaN     USDT  57.07262111         0.0005       tier              0.005           0                   0             0     crossed        10000            0         57.07262111   BTC-USDT              0
        """
        for _ in range(max_try_amount):
            try:
                future_info = self.__ccxt_provider.ccxt_object_for_fetching.futures_get_accounts()['info']
                df = pd.DataFrame(future_info, dtype=float).T  # 将数据转化为df格式
                return df
            except Exception as e:
                print('通过ccxt的通过futures_get_accounts获取所有合约账户信息，失败，稍后重试：\n', e)
                time.sleep(self.medium_sleep_time)

        raise ValueError('通过ccxt的通过futures_get_accounts获取所有合约账户信息，失败次数过多，程序Raise Error')

    def fetch_future_position(self, max_try_amount=5):
        """
        ==== 通过ccxt、交易所接口获取合约账户持仓信息
        :param exchange:
        :param max_try_amount:
        :return:
        本程序使用okex3中“交割合约API”、“所有合约持仓信息”接口，获取合约账户所有合约的持仓信息。
        使用ccxt函数：exchange.futures_get_position()
        请求此接口，okex服务器会在其数据库中遍历所有币对下的持仓数据，有大量的性能消耗，请求频率较低，时间较长。

        接口返回数据格式样例：
        {'result': True, 'holding':
        [[{'long_qty': '1', 'long_avail_qty': '1', 'long_margin': '0.027094', 'long_liqui_price': '241.07', 'long_pnl_ratio': '-0.0636223', 'long_avg_cost': '265.63', 'long_settlement_price': '265.63', 'realised_pnl': '0.00051826', 'short_qty': '0', 'short_avail_qty': '0', 'short_margin': '0', 'short_liqui_price': '0', 'short_pnl_ratio': '0.0714716', 'short_avg_cost': '265.84', 'short_settlement_price': '265.84', 'instrument_id': 'ETH-USDT-200327', 'long_leverage': '10', 'short_leverage': '10', 'created_at': '2020-02-22T08:02:04.469Z', 'updated_at': '2020-02-22T08:42:02.484Z', 'margin_mode': 'fixed', 'short_margin_ratio': '10000.0', 'short_maint_margin_ratio': '0.01', 'short_pnl': '0.0', 'short_unrealised_pnl': '0.0', 'long_margin_ratio': '0.09624915', 'long_maint_margin_ratio': '0.01', 'long_pnl': '-0.00169', 'long_unrealised_pnl': '-0.00169', 'long_settled_pnl': '0', 'short_settled_pnl': '0', 'last': '264.08'},
        {'long_qty': '1', 'long_avail_qty': '1', 'long_margin': '0.04127', 'long_liqui_price': '3.753', 'long_pnl_ratio': '-0.0048473', 'long_avg_cost': '4.126', 'long_settlement_price': '4.126', 'realised_pnl': '-0.0010528', 'short_qty': '1', 'short_avail_qty': '1', 'short_margin': '0.0404', 'short_liqui_price': '4.476', 'short_pnl_ratio': '-0.0097087', 'short_avg_cost': '4.12', 'short_settlement_price': '4.12', 'instrument_id': 'EOS-USDT-200327', 'long_leverage': '10', 'short_leverage': '10', 'created_at': '2020-02-20T06:17:21.890Z', 'updated_at': '2020-02-22T09:53:15.931Z', 'margin_mode': 'fixed', 'short_margin_ratio': '0.09699321', 'short_maint_margin_ratio': '0.01', 'short_pnl': '-4.0E-4', 'short_unrealised_pnl': '-4.0E-4', 'long_margin_ratio': '0.09958778', 'long_maint_margin_ratio': '0.01', 'long_pnl': '-2.0E-4', 'long_unrealised_pnl': '-2.0E-4', 'long_settled_pnl': '0', 'short_settled_pnl': '0', 'last': '4.123'}],
        [{'long_qty': '0', 'long_avail_qty': '0', 'long_avg_cost': '0', 'long_settlement_price': '0', 'realised_pnl': '0', 'short_qty': '3', 'short_avail_qty': '3', 'short_avg_cost': '4.53509442', 'short_settlement_price': '4.114', 'liquidation_price': '130311.677', 'instrument_id': 'EOS-USD-200327', 'leverage': '10', 'created_at': '2020-02-18T06:42:29.924Z', 'updated_at': '2020-02-22T08:00:16.315Z', 'margin_mode': 'crossed', 'short_margin': '0.72184793', 'short_pnl': '0.60340204', 'short_pnl_ratio': '0.9121617', 'short_unrealised_pnl': '-0.07369376', 'long_margin': '0.0', 'long_pnl': '0.0', 'long_pnl_ratio': '0.0', 'long_unrealised_pnl': '0.0', 'long_settled_pnl': '0', 'short_settled_pnl': '0.6770958', 'last': '4.156'},
        {'long_qty': '0', 'long_avail_qty': '0', 'long_avg_cost': '75.37', 'long_settlement_price': '75.37', 'realised_pnl': '-0.00029526', 'short_qty': '0', 'short_avail_qty': '0', 'short_avg_cost': '0', 'short_settlement_price': '0', 'liquidation_price': '0.00', 'instrument_id': 'LTC-USDT-200327', 'leverage': '3', 'created_at': '2020-02-22T08:02:07.424Z', 'updated_at': '2020-02-22T08:07:05.078Z', 'margin_mode': 'crossed', 'short_margin': '0.0', 'short_pnl': '0.0', 'short_pnl_ratio': '0.0', 'short_unrealised_pnl': '0.0', 'long_margin': '0.0', 'long_pnl': '0.0', 'long_pnl_ratio': '0.01791165', 'long_unrealised_pnl': '0.0', 'long_settled_pnl': '0', 'short_settled_pnl': '0', 'last': '75.82'}]]}
        返回结果说明：
        1.币本位合约和usdt本位合约的信息会一起返回。例如holding中第一行返回的是usdt本位合约数据，第二行返回的是币本位合约的数据
        2.一个币种同时有多头或者空头，也会在一行里面返回数据

        本函数输出示例：
            created_at    instrument_id     last  leverage  liquidation_price  long_avail_qty  long_avg_cost  long_leverage  long_liqui_price  long_maint_margin_ratio  long_margin  long_margin_ratio  long_pnl  long_pnl_ratio  long_qty  long_settled_pnl  long_settlement_price  long_unrealised_pnl margin_mode  realised_pnl  short_avail_qty  short_avg_cost  short_leverage  short_liqui_price  short_maint_margin_ratio  short_margin  short_margin_ratio  short_pnl  short_pnl_ratio  short_qty  short_settled_pnl  short_settlement_price  short_unrealised_pnl                updated_at
        eth-usdt  2020-02-22T08:02:04.469Z  ETH-USDT-200327  264.090       NaN                NaN             1.0        265.630           10.0           241.070                     0.01     0.027094           0.096762  -0.00154       -0.057975       1.0               0.0                265.630             -0.00154       fixed      0.000518              0.0      265.840000            10.0              0.000                      0.01      0.000000        10000.000000   0.000000         0.065829        0.0           0.000000                 265.840               0.00000  2020-02-22T08:42:02.484Z
        eos-usdt  2020-02-20T06:17:21.890Z  EOS-USDT-200327    4.127       NaN                NaN             1.0          4.126           10.0             3.753                     0.01     0.041270           0.100024   0.00000        0.000000       1.0               0.0                  4.126              0.00000       fixed     -0.001053              1.0        4.120000            10.0              4.476                      0.01      0.040400            0.096461  -0.000600        -0.014563        1.0           0.000000                   4.120              -0.00060  2020-02-22T09:53:15.931Z
        eos-usd   2020-02-18T06:42:29.924Z   EOS-USD-200327    4.158      10.0         130311.677             0.0          0.000            NaN               NaN                      NaN     0.000000                NaN   0.00000        0.000000       0.0               0.0                  0.000              0.00000     crossed      0.000000              3.0        4.535094             NaN                NaN                       NaN      0.721674                 NaN   0.601666         0.909537        3.0           0.677096                   4.114              -0.07543  2020-02-22T08:00:16.315Z
        ltc-usdt  2020-02-22T08:02p:07.424Z  LTC-USDT-200327   75.910       3.0              0.000             0.0         75.370            NaN               NaN                      NaN     0.000000                NaN   0.00000        0.020698       0.0               0.0                 75.370              0.00000     crossed     -0.000295              0.0        0.000000             NaN                NaN                       NaN      0.000000                 NaN   0.000000         0.000000        0.0           0.000000                   0.000               0.00000  2020-02-22T08:07:05.078Z
        """
        for _ in range(max_try_amount):
            try:
                # 获取数据
                position_info = self.__ccxt_provider.ccxt_object_for_fetching.futures_get_position()['holding']
                # 整理数据
                df = pd.DataFrame(sum(position_info, []), dtype=float)
                # 防止账户初始化时出错
                if "instrument_id" in df.columns:
                    df['index'] = df['instrument_id'].str[:-7].str.lower()
                    df.set_index(keys='index', inplace=True)
                    df.index.name = None
                return df
            except Exception as e:
                print('通过ccxt的通过futures_get_position获取所有合约的持仓信息，失败，稍后重试。失败原因：\n', e)
                time.sleep(self.medium_sleep_time)

        raise ValueError('通过ccxt的通过futures_get_position获取所有合约的持仓信息，失败次数过多，程序Raise Error')

    def update_symbol_info(self, symbol_info, instrument_id_list, index_mapping_dict):
        """
        ==== 根据账户信息、持仓信息，更新symbol_info ===
        本函数通过ccxt_fetch_future_account()获取合约账户信息，ccxt_fetch_future_position()获取合约账户持仓信息，并用这些信息更新symbol_config
        :param exchange:
        :param symbol_info:
        :param instrument_id_list:
        :return:
        """

        # 通过交易所接口获取合约账户信息
        future_account = self.fetch_future_account()
        # 将账户信息和symbol_info合并
        if future_account.empty is False:
            future_account.rename(index=index_mapping_dict, inplace=True)
            symbol_info['账户权益'] = future_account['equity']

        # 通过交易所接口获取合约账户持仓信息
        future_position = self.fetch_future_position()
        # 将持仓信息和symbol_info合并
        if future_position.empty is False:
            future_position.rename(index=index_mapping_dict, inplace=True)
            # 去除无关持仓：账户中可能存在其他合约的持仓信息，这些合约不在symbol_config中，将其删除。
            future_position = future_position[future_position.instrument_id.isin(instrument_id_list)]

            # 从future_position中获取原始数据
            symbol_info['最大杠杆'] = future_position['leverage']
            symbol_info['当前价格'] = future_position['last']

            symbol_info['多头持仓量'] = future_position['long_qty']
            symbol_info['多头均价'] = future_position['long_avg_cost']
            symbol_info['多头收益率'] = future_position['long_pnl_ratio']
            symbol_info['多头收益'] = future_position['long_pnl']

            symbol_info['空头持仓量'] = future_position['short_qty']
            symbol_info['空头均价'] = future_position['short_avg_cost']
            symbol_info['空头收益率'] = future_position['short_pnl_ratio']
            symbol_info['空头收益'] = future_position['short_pnl']

            # 检验是否同时持有多头和空头
            temp = symbol_info[(symbol_info['多头持仓量'] > 0) & (symbol_info['空头持仓量'] > 0)]
            if temp.empty is False:
                raise ValueError('{} 当前账户同时存在多仓和空仓，请平掉其中至少一个仓位后再运行程序，程序exit'.format(list(temp.index)))

            # 整理原始数据，计算需要的数据
            # 多头、空头的index
            long_index = symbol_info[symbol_info['多头持仓量'] > 0].index
            short_index = symbol_info[symbol_info['空头持仓量'] > 0].index
            # 账户持仓方向
            symbol_info.loc[long_index, '持仓方向'] = 1
            symbol_info.loc[short_index, '持仓方向'] = -1
            symbol_info['持仓方向'].fillna(value=0, inplace=True)
            # 账户持仓量
            symbol_info.loc[long_index, '持仓量'] = symbol_info['多头持仓量']
            symbol_info.loc[short_index, '持仓量'] = symbol_info['空头持仓量']
            # 持仓均价
            symbol_info.loc[long_index, '持仓均价'] = symbol_info['多头均价']
            symbol_info.loc[short_index, '持仓均价'] = symbol_info['空头均价']
            # 持仓收益率
            symbol_info.loc[long_index, '持仓收益率'] = symbol_info['多头收益率']
            symbol_info.loc[short_index, '持仓收益率'] = symbol_info['空头收益率']
            # 持仓收益
            symbol_info.loc[long_index, '持仓收益'] = symbol_info['多头收益']
            symbol_info.loc[short_index, '持仓收益'] = symbol_info['空头收益']
            # 删除不必要的列
            symbol_info.drop(['多头持仓量', '多头均价', '空头持仓量', '空头均价', '多头收益率', '空头收益率', '多头收益', '空头收益'],
                             axis=1, inplace=True)
        else:
            # 当future_position为空时，将持仓方向的控制填充为0，防止之后判定信号时出错
            symbol_info['持仓方向'].fillna(value=0, inplace=True)

        return symbol_info

    def fetch_account_equity(self, symbol, max_try_amount=5):
        """
        # ===获取指定账户，例如btcusdt合约，目前的现金余额。
        使用okex私有函数，GET/api/futures/v3/accounts/<underlying>，获取指定币种的账户现金余额。
        :param exchange:
        :param underlying:  例如btc-usd，btc-usdt
        :param max_try_amount:
        :return:
        """
        for _ in range(max_try_amount):
            try:
                result = self.__ccxt_provider.ccxt_object_for_fetching.futures_get_accounts_underlying(params={"underlying": symbol.lower()})
                return float(result['equity'])
            except Exception as e:
                print(e)
                print('ccxt_update_account_equity函数获取账户可用余额失败，稍后重试')
                time.sleep(self.short_sleep_time)

    def cal_order_size(self, coin_pair_str, holding, signal_price, equity_balance, leverage, volatility_ratio=0.98):
        """
        根据实际持仓以及杠杆数，计算实际开仓张数
        :param symbol:
        :param symbol_info:
        :param leverage:
        :param volatility_ratio:
        :return:
        """
        # 当账户目前有持仓的时候，必定是要平仓，所以直接返回持仓量即可
        if pd.notna(holding):  # 不为空
            return holding

        # 当账户没有持仓时，是开仓
        price = signal_price
        coin_value = [coin_value_table[x] for x in coin_value_table if (x + '-').upper() in coin_pair_str.upper()][0]  # 取出对应面值 (区分 USDT/USD)
        # 不超过账户最大杠杆
        l = float(leverage)
        size = math.floor(equity_balance * l * volatility_ratio / (price * coin_value))
        return max(size, 1)  # 防止出现size为情形0，设置最小下单量为1

    def cal_order_price(self, price, order_type, ratio=0.02):
        """ 为了达到成交的目的，计算实际委托价格会向上或者向下浮动一定比例默认为0.02 """
        if order_type in [1, 4]:
            return price * (1 + ratio)
        elif order_type in [2, 3]:
            return price * (1 - ratio)

    def okex_future_place_order(self, underlying, coin_pair_str, symbol_signals, signal_price, holding, equity_balance, leverage, max_try_amount=5):
        """
        # 在合约市场下单
        :param symbol_info:
        :param symbol_config:
        :param symbol_signal:
        :param max_try_amount:
        :return:
        """
        # 下单参数
        params = {
            'instrument_id': coin_pair_str  # 合约代码
        }

        order_id_list = []
        # 按照交易信号下单
        for order_type in symbol_signals:
            update_price_flag = False  # 当触发限价条件时会设置为True
            for i in range(max_try_amount):
                try:
                    # 当只要开仓或者平仓时，直接下单操作即可。但当本周期即需要平仓，又需要开仓时，需要在平完仓之后，
                    # 重新评估下账户资金，然后根据账户资金计算开仓账户然后开仓。下面这行代码即处理这个情形。
                    # "长度为2的判定"定位【平空，开多】或【平多，开空】两种情形，"下单类型判定"定位 处于开仓的情形。
                    if len(symbol_signals) == 2 and order_type in [1, 2]:  # 当两个条件同时满足时，说明当前处于平仓后，需要再开仓的阶段。
                        time.sleep(self.short_sleep_time)  # 短暂的休息1s，防止之平仓后，账户没有更新
                        equity_balance = self.fetch_account_equity(underlying)

                    # 确定下单参数
                    params['type'] = str(order_type)
                    params['price'] = self.cal_order_price(signal_price, order_type)
                    params['size'] = int(self.cal_order_size(coin_pair_str, holding, signal_price, float(equity_balance), leverage))

                    if update_price_flag:
                        # {'instrument_id': 'BTC-USDT-200626',
                        #  'highest': '7088.5',
                        #  'lowest': '6674.2',
                        #  'timestamp': '2020-04-22T06:21:12.441Z'}
                        # 获取当前限价
                        response = self.__ccxt_provider.ccxt_object_for_fetching.futures_get_instruments_instrument_id_price_limit({"instrument_id": coin_pair_str})
                        # 依据下单类型来判定，所用的价格
                        order_type_tmp = int(params['type'])
                        # 开多和平空，对应买入合约取最高
                        if order_type_tmp in [1, 4]:
                            params['price'] = float(response['highest'])
                        elif order_type_tmp in [2, 3]:
                            params['price'] = float(response['lowest'])
                        update_price_flag = False

                    print('开始下单：', datetime.now())
                    order_info = self.__ccxt_provider.ccxt_object_for_order.futures_post_order(params)
                    order_id_list.append(order_info['order_id'])
                    print(order_info, '下单完成：', datetime.now())
                    break

                except Exception as e:
                    print(traceback.format_exc())
                    print(coin_pair_str, '下单失败，稍等后继续尝试')
                    time.sleep(self.short_sleep_time)
                    '''
                    okex {"error_message":"Order price cannot be more than 103% or less than 97% of the previous minute price","code":32019,"error_code":"32019",
                    "message":"Order price cannot be more than 103% or less than 97% of the previous minute price"}
                    '''
                    # error code 与错误是一一对应的关系，32019代表相关错误
                    if "32019" in str(e):
                        update_price_flag = True

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
                        'instrument_id': coin_pair_str,
                        'order_id': order_id
                    }
                    order_info = self.__ccxt_provider.ccxt_object_for_query.futures_get_orders_instrument_id_order_id(para)
                    break
                except Exception as e:
                    print(e)
                    print('根据订单号获取订单信息失败，稍后重试')
                    time.sleep(self.medium_sleep_time)
                    if i == max_try_amount - 1:
                        raise ValueError('重试次数过多，获取订单信息失败，程序退出')

            if order_info:
                info_dict = {
                    "订单状态": okex_order_state[order_info["state"]],
                    "开仓方向": okex_order_type[order_info["type"]],
                    "委托数量": order_info["size"],
                    "成交数量": order_info["filled_qty"],
                    "委托价格": order_info["price"],
                    "成交均价": order_info["price_avg"],
                    "委托时间": order_info["timestamp"]
                }
                if okex_order_state[order_info["state"]] == '失败':
                    print('下单失败')
                all_order_infos[order_id] = info_dict
            else:
                print('根据订单号获取订单信息失败次数超过max_try_amount，发送钉钉')

        return all_order_infos
