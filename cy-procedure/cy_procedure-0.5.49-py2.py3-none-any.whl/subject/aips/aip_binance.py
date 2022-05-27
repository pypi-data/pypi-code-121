from .aip_base import *
from ..exchange.binance import *


class BinanceAIP(AIPBase):
    """币安定投"""

    def __init__(self,
                 coin_pair,
                 time_frame,
                 signal_provider,
                 day_of_week,
                 ma_periods,
                 trader_provider,
                 invest_base_amount,
                 recorder,
                 debug=False,
                 fee_percent=0):
        super().__init__(coin_pair, time_frame, signal_provider, day_of_week, ma_periods,
                         trader_provider, invest_base_amount, recorder, debug, fee_percent)
        self.__handler = BinanceHandler(trader_provider)

    def _prepare_to_buying(self, invest_amount):
        """下单前准备，失败自行记录"""
        try:
            spot_balance = self._fetch_base_coin_balance()
            amount_difference = self._truncate(invest_amount - spot_balance, self.precision_amount)
            if amount_difference > 0:
                # 取活期产品
                lending_product = self.__handler.daily_lending_product(self.coin_pair.base_coin)
                if lending_product is None:
                    self.recorder.append_summary_log(F'找不到 {self.coin_pair.base_coin} 活期产品')
                    return
                # 划转到现货
                print(lending_product)
                product_id = lending_product['productId']
                # 划转,取出来
                result = self.__handler.redeem_daily_lending_product(product_id, amount_difference)
                if result is None:
                    self.recorder.append_summary_log(F'{self.coin_pair.base_coin} 划转失败')
        except Exception as e:
            self.recorder.append_summary_log(F'**交易前准备失败，{str(e)}**')

    def _place_buying_order(self, invest_amount):
        """下单，成功返回：
        {
        'price': 123,
        'cost': 123,
        'amount': 123
        }"""
        try:
            print(F"下单参数: {self.coin_pair.formatted()}, {invest_amount}")
            logger = TraderLogger(self.trader_provicer.display_name, self.coin_pair.formatted(), 'Spot', self.recorder)
            return self.__handler.handle_spot_buying(self.coin_pair, invest_amount, logger)
        except Exception as e:
            self.recorder.record_summary_log("下单失败，" + str(e))

    def _rollback_when_order_failed(self, invest_amount):
        """下单失败后回滚"""
        try:
            spot_balance = self._fetch_base_coin_balance()
            self.__transfer_to_daily_production(self.coin_pair.base_coin, spot_balance)
        except Exception:
            self.recorder.append_summary_log('**回滚划转 {} 失败**'.format(self.coin_pair.base_coin.upper()))

    def _finishing_aip(self, remaining_base_coin_amount):
        """完成定投后的收尾工作"""
        try:
            self.__transfer_to_daily_production(self.coin_pair.base_coin, remaining_base_coin_amount)
            self.__transfer_to_daily_production(self.coin_pair.trade_coin, self._fetch_trade_coin_balance())
        except Exception:
            self.recorder.record_summary_log('**定投结束后划转失败**')

    def __transfer_to_daily_production(self, coin, amount):
        """划转到活期"""
        try:
            lending_product = self.__handler.daily_lending_product(coin)
            if lending_product is None:
                print(F'找不到 {coin} 活期产品')
            else:
                product_id = lending_product['productId']
                print(lending_product)
                # 划转
                if amount > 0:
                    result = self.__handler.purchase_daily_lending_product(product_id, amount).get('purchaseId')
                    if result is None:
                        print(F'购买 {coin} 活期失败')
        except Exception as e:
            print(F'**划转 {coin} 到活期失败，{str(e)}**')
