#!/usr/bin/env python3
# coding: utf-8

import ccxt
import urllib.parse, urllib.request
from urllib.parse import urljoin, urlencode
import json, hashlib, hmac, time
from datetime import datetime
import requests
import calendar

import pandas as pd
import numpy as np

from datetime import timedelta

from binance.client import Client

import math

class BinanceSpotBot(object):

    def __init__(self, BINANCE_PUBLIC, BINANCE_PRIVATE):

        self.client = Client(BINANCE_PUBLIC, BINANCE_PRIVATE)
        self.apiKey = BINANCE_PUBLIC
        self.secret = BINANCE_PRIVATE
        Binancecle2 = {
            'api_key': BINANCE_PUBLIC,
            'api_secret': BINANCE_PRIVATE,
        }
        print('Connexion to Binance Future')
        exchange_id = 'binance'
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({
            'apiKey': Binancecle2['api_key'],
            'secret': Binancecle2['api_secret'],
            'timeout': 10000,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'},
        })


    def get_spot_universe(self):
        tickers_universe = self.client.get_all_tickers()
        return tickers_universe

    def get_ticker_info(self,filtering_stub = ['PAX','ZAR','BKRW']):
        ticker_info = self.client.get_ticker()
        ticker_info_df = pd.DataFrame(ticker_info)
        ticker_info_df['priceChangePercent']=ticker_info_df['priceChangePercent'].astype(float)
        ticker_info_df = ticker_info_df.sort_values(by=['priceChangePercent'],ascending=False)
        def is_tradable(row):
            tradable = True
            for stub in filtering_stub:
                if stub in row['symbol']:
                    tradable = False
            return tradable

        ticker_info_df['tradable'] = ticker_info_df.apply(is_tradable, axis=1)
        ticker_info_df = ticker_info_df[ticker_info_df['tradable']].copy()
        return ticker_info_df



    def get_generator_hourly_ohlc(self, pair, starting_date):
        encours_date = datetime.now()
        klines = []
        while encours_date >= starting_date:
#            print(f'fetching {encours_date}')
            kline = self.client.get_historical_klines_generator(pair, Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC")
            klines.append(list(kline))
            encours_date = encours_date - timedelta(days=1)
        print('done')
        flat_list = [item for sublist in klines for item in sublist]
        dataframe = pd.DataFrame(flat_list)

        # Calling DataFrame constructor on list
        # with indices and columns specified
        columns_names = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_vol',
                             'ntrades',
                             'takerbuy_base_asset_vol', 'takerbuy_quote_asset_vol', 'ignore']
        dataframe.columns = columns_names
        dataframe['time'] = pd.to_datetime(dataframe['time'], unit='ms')
        dataframe = dataframe.sort_values(by=['time'])
        dataframe = dataframe.rename(columns={"time": "date"}, errors="raise")
        dataframe = dataframe.set_index(dataframe['date'])
        dataframe = dataframe[['open', 'high', 'low', 'close', 'volume']].copy()
        print('size fetched')
        print(dataframe.shape)
        return dataframe


    def get_hourly_live_ohlc(self, pair):
        rbtc = requests.get('https://min-api.cryptocompare.com/data/v2/histoday?fsym={}&tsym=USD&limit=1500'.format(pair.replace('USDT','')))
        df = pd.DataFrame(json.loads(rbtc.text)['Data']['Data'])
        df = df.set_index('time')
        df.drop(columns=['high', 'low', 'volumefrom', 'volumeto', 'open', 'conversionType', 'conversionSymbol'],
                inplace=True)
        df.rename(columns={'close': pair}, inplace=True)
        print('data loaded')

        df = df.reset_index()
        df['Date'] = df.apply(lambda x: datetime.datetime.fromtimestamp(x['time'], tz=datetime.timezone.utc), axis=1)
        df['weekday'] = df.apply(lambda x: datetime.datetime.date(x['Date']).weekday(), axis=1)
        df = df.set_index('Date')
        df.drop(columns=['time'], inplace=True)
        return df

    def get_hourly_ohlc(self, pair, starting_date, ending_date):
        #starting_date_string = starting_date.strftime('%m/%d/%y')
        #ending_date_string = ending_date.strftime('%m/%d/%y')
        starting_date_string = starting_date.strftime('%d %b, %Y')
        ending_date_string = ending_date.strftime('%d %b, %Y')
        dataframe = self.client.get_historical_klines(pair, Client.KLINE_INTERVAL_1HOUR, starting_date_string, ending_date_string)
        dataframe = pd.DataFrame(dataframe)
        names = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_vol', 'ntrades',
         'takerbuy_base_asset_vol', 'takerbuy_quote_asset_vol', 'ignore']
        if len(dataframe.columns)!=len(names):
            raise('Hoy shit')

        dataframe.columns = names
        dataframe['time'] = pd.to_datetime(dataframe['time'], unit='ms')
        dataframe = dataframe.sort_values(by=['time'])
        dataframe = dataframe.rename(columns={"time": "date"}, errors="raise")
        dataframe = dataframe.set_index(dataframe['date'])
        dataframe = dataframe[['open','high','low','close','volume']].copy()


        print('size fetched')
        print(dataframe.shape)
        return dataframe


    def get_ticker_info_usdt(self, volume_limit = 250, to_ban = ['TLMUSDT','BCHSVUSDT','USDTZAR','USDTTRY','USDTBIDR','USDTIDRT','USDTBVND','USDTRUB','USDTNGN','STRAXUSDT']):#'SRMUSDT','PAXGUSDT',]):
        ticker_info = self.client.get_ticker()
        ticker_info_df = pd.DataFrame(ticker_info)
        def is_tradable(row):
            tradable = False
            if 'USDT' in row['symbol'] and not row['symbol'].startswith('USDT') and 'UP' not in row['symbol'] and 'DOWN' not in row['symbol'] and 'BULL' not in row['symbol'] and row['symbol'] not in to_ban:
                tradable = True
            return tradable
        ticker_info_df['tradable'] = ticker_info_df.apply(is_tradable, axis=1)
        ticker_info_df = ticker_info_df[ticker_info_df['tradable']].copy()
        ticker_info_df = ticker_info_df.sort_values(by=['volume'], ascending=False)
        ticker_info_df = ticker_info_df.iloc[:volume_limit]
        ticker_info_df['priceChangePercent']=ticker_info_df['priceChangePercent'].astype(float)
        ticker_info_df = ticker_info_df.sort_values(by=['priceChangePercent'],ascending=False)


        return ticker_info_df

    def get_best_tickers(self):
        tickers_universe = self.client.get_all_tickers()
        return tickers_universe


    def get_spot_underlyings(self):
        account = self.client.get_account()
        spot_universe = [asset['asset'] for asset in account['balances']]
        return spot_universe

    def get_spot_balance_df(self,):
        account = self.client.get_account()
        balances_df = pd.DataFrame(account['balances'])
        return balances_df

    def get_spot_balance(self,):
        account = self.client.get_account()
        return account['balances']

    def get_last_ticker_underlyings(self, ticker):
        ticker_info = self.client.get_ticker(symbol = ticker)
        return ticker_info

    def get_total_valo(self):
        spot_balances = self.get_free_spot_balance()
        total_valo = 0.
        for me_ticker, me_balance in spot_balances.items():
            if me_ticker != 'USDT':
                me_pair = me_ticker + 'USDT'
                print(f'pair {me_pair}')
                ticker_info = self.get_last_ticker_underlyings(me_pair)
                price = float(ticker_info['bidPrice'])
                print(f'ticker {me_ticker} price {price}')
                total_valo = total_valo + me_balance * price
            else:
                total_valo = total_valo + me_balance
        return total_valo

    def enter_coins(self, quantities_to_enter=None):
        for me_ticker, me_quantity in quantities_to_enter.items():
            me_pair=me_ticker + 'USDT'
            info = self.client.get_symbol_info(me_pair)
            minQty = info['filters'][2]['minQty']
            to_roundto = -math.log10(float(minQty))
#            factor = 1/float(minQty)
            factor = math.pow(10,to_roundto)
            me_quantity= math.floor(me_quantity * factor) / factor
            if me_quantity > float(minQty):
                not_success = True
                counter = 0
                while not_success and counter<=5:
                    try:
                        print(f'buying {me_ticker} for {me_quantity}')
                        order = self.client.order_market_buy(symbol=me_pair, quantity=me_quantity)
                        print(order)
                        not_success=False
                    except Exception as inst:
                        print(inst)
                        me_quantity = me_quantity - float(minQty)
                        counter = counter+1
                if counter > 5 :
                    raise Exception('holy guacamole')


    def liquidate_coins(self, quantities_to_liquidate=None):
        for me_ticker, me_quantity in quantities_to_liquidate.items():
            me_pair=me_ticker + 'USDT'
            info = self.client.get_symbol_info(me_pair)
            minQty = info['filters'][2]['minQty']
            to_roundto = -math.log10(float(minQty))
            #factor = 1/float(minQty)
            factor = math.pow(10, to_roundto)
            me_quantity= math.floor(me_quantity * factor) / factor
            if me_quantity>float(minQty):
                print(f'selling {me_ticker} for {me_quantity}')
                try:
                    order = self.client.order_market_sell(symbol=me_ticker + 'USDT', quantity=me_quantity)
                    print(order)
                except Exception as inst:
                    print(inst)



    def get_coins_to_enter(self, signals):
        old_quantities = self.get_free_spot_balance()
        total_valo = 0.
        spot_prices = {}
        old_tickers = list(old_quantities.keys())
        new_tickers = list(signals.keys())
        for me_ticker, me_balance in old_quantities.items():
            #only the USDT is reinvested
            if me_ticker == 'USDT':
                total_valo = total_valo + me_balance

        for me_ticker in signals.keys():
            me_pair = me_ticker + 'USDT'
            print(f'pair {me_pair}')
            ticker_info = self.get_last_ticker_underlyings(me_pair)
            price = float(ticker_info['bidPrice'])
            print(f'ticker {me_ticker} price {price}')
            spot_prices[me_ticker] = price
        coin_to_enter_number = 0
        for me_ticker, me_sig in signals.items():
            if me_ticker not in old_quantities.keys():
                coin_to_enter_number = coin_to_enter_number+1

        usdt_new_quantities = {}
        ticker_new_quantities = {}
        for me_ticker, me_sig in signals.items():
            if me_ticker not in old_quantities.keys():
                usdt_new_quantities[me_ticker] = total_valo/coin_to_enter_number
                ticker_new_quantities[me_ticker] = usdt_new_quantities[me_ticker] /spot_prices[me_ticker]

        return ticker_new_quantities


    def get_coins_to_liquidate(self, signals):
        old_quantities = self.get_free_spot_balance()
        total_valo = 0.
        spot_prices = {}
        old_tickers = list(old_quantities.keys())
        new_tickers = list(signals.keys())
        for me_ticker, me_balance in old_quantities.items():
            if me_ticker != 'USDT':
                me_pair = me_ticker + 'USDT'
                print(f'pair {me_pair}')
                ticker_info = self.get_last_ticker_underlyings(me_pair)
                price = float(ticker_info['bidPrice'])
                print(f'ticker {me_ticker} price {price}')
                spot_prices[me_ticker] = price
                total_valo = total_valo + me_balance * price
            else:
                total_valo = total_valo + me_balance

        for me_ticker in signals.keys():
            me_pair = me_ticker + 'USDT'
            print(f'pair {me_pair}')
            ticker_info = self.get_last_ticker_underlyings(me_pair)
            price = float(ticker_info['bidPrice'])
            print(f'ticker {me_ticker} price {price}')
            spot_prices[me_ticker] = price

        usdt_new_quantities = {}
        ticker_new_quantities = {}
        for me_ticker, me_sig in signals.items():
            usdt_new_quantities[me_ticker] = me_sig*total_valo
            ticker_new_quantities[me_ticker] = me_sig*total_valo/spot_prices[me_ticker]

        ##### what is in old but not in new
        liquidations = {}
        for me_ticker, me_quantity in old_quantities.items():
            if me_ticker not in ticker_new_quantities.keys():
                print(f'liquidating quantity {me_ticker} {me_quantity}')
                if me_ticker != 'USDT':
                    if abs(me_quantity) > 1e-3:
                        liquidations[me_ticker]=me_quantity
            # else :
            #     quantity_to_pass = ticker_new_quantities[me_ticker] - old_quantities[me_ticker]
            #     print(f'passing quantity {me_ticker} {quantity_to_pass}')
        return liquidations

    def get_quantity_to_pass(self,signals=None):
        old_quantities = self.get_free_spot_balance()
        total_valo = 0.
        spot_prices = {}

        old_tickers = list(old_quantities.keys())
        old_tickers = [old_tick for old_tick in old_tickers if old_tick != 'USDT']
        new_tickers = list(signals.keys())

        for me_ticker, me_balance in old_quantities.items():
            if me_ticker != 'USDT':
                me_pair = me_ticker + 'USDT'
                print(f'pair {me_pair}')
                ticker_info = self.get_last_ticker_underlyings(me_pair)
                price = float(ticker_info['bidPrice'])
                print(f'ticker {me_ticker} price {price}')
                spot_prices[me_ticker] = price
                total_valo = total_valo + me_balance * price
            else:
                total_valo = total_valo + me_balance

        for me_ticker in signals.keys():
            me_pair = me_ticker + 'USDT'
            print(f'pair {me_pair}')
            ticker_info = self.get_last_ticker_underlyings(me_pair)
            price = float(ticker_info['bidPrice'])
            print(f'ticker {me_ticker} price {price}')
            spot_prices[me_ticker] = price

        usdt_new_quantities = {}
        ticker_new_quantities = {}
        for me_ticker, me_sig in signals.items():
            usdt_new_quantities[me_ticker] = me_sig*total_valo
            ticker_new_quantities[me_ticker] = me_sig*total_valo/spot_prices[me_ticker]

        ##### what is in old but not in new
        liquidations = {}
        for me_ticker, me_quantity in old_quantities.items():
            if me_ticker not in ticker_new_quantities.keys():
                print(f'liquidating quantity {me_ticker} {me_quantity}')
                liquidations[me_ticker]=me_quantity
            # else :
            #     quantity_to_pass = ticker_new_quantities[me_ticker] - old_quantities[me_ticker]
            #     print(f'passing quantity {me_ticker} {quantity_to_pass}')

        enterings = {}
        ##### what is in new but not in old
        for me_ticker, me_quantity in ticker_new_quantities.items():
            if me_ticker not in old_quantities.keys():
                print(f'entering quantity {me_ticker} {me_quantity}')
                enterings[me_ticker] = me_quantity

        switchs = {}
        for me_ticker, me_quantity in old_quantities.items():
            if me_ticker in ticker_new_quantities.keys():
                quantity_to_pass = ticker_new_quantities[me_ticker] - old_quantities[me_ticker]
                print(f'passing quantity {me_ticker} {quantity_to_pass}')
                switchs[me_ticker] = me_quantity

        return liquidations,enterings,switchs


    def get_free_spot_balance(self,):
        account = self.client.get_account()
        balances = account['balances']
        free_positive_balances={}
        for asset_balance in balances :
            if float(asset_balance['free'])>0:
                me_quantity =float(asset_balance['free'])
                if abs(me_quantity)>1e-3:
                    free_positive_balances[asset_balance['asset']] = me_quantity
        return free_positive_balances

    def get_all_spot_open_orders(self):
        me_orders = self.client.get_open_orders()
        #return pd.DataFrame(me_orders)
        return me_orders

    def cancel_all_spot_open_orders(self):
        for me_order in self.get_all_spot_open_orders():
            self.client.cancel_order(symbol = me_order['symbol'], orderId = me_order['orderId'])

    def get_spot_orders(self, pair):
        me_orders = self.client.get_all_orders(symbol = pair)
        return me_orders

    def cancel_all_spot_orders(self,):
        all_orders = self.client.get_all_orders()
        print(all_orders)

    # def cancel_all_order(self, pair):
    #     Cleaner = self.exchange.fetch_open_orders(pair)
    #     L = len(Cleaner)
    #     if L > 0:
    #         for i in range(0, L):
    #             self.exchange.cancel_order(Cleaner[i]['info']['orderId'], 'BTC/USDT')
    #
    # def cancel_all_orders(self):
    #     self.cancel_all_order('BTC/USDT')
    #     self.cancel_all_order('ETH/USDT')
    #     self.cancel_all_order('LTC/USDT')
    #     self.cancel_all_order('EOS/USDT')
    #     self.cancel_all_order('XRP/USDT')
    #     self.cancel_all_order('BCH/USDT')
    #     self.cancel_all_order('TRX/USDT')


    def get_futures_balance_history(self, start_time, end_time):
        startTime = int(start_time.timestamp() * 1000)
        endTime = int(end_time.timestamp() * 1000)

        BASE_URL = 'https://api.binance.com'
        PATH = '/sapi/v1/accountSnapshot'

        headers = {
            'X-MBX-APIKEY': self.apiKey
        }
        timestamp = int(time.time() * 1000)

        params = {
            'type': 'FUTURES',
            'recvWindow': 60000,
            'timestamp': timestamp,
            'startTime': startTime,
            'endTime': endTime,
            'limit': 300

        }
        query_string = urllib.parse.urlencode(params)
        params['signature'] = hmac.new(self.secret.encode('utf-8'), query_string.encode('utf-8'),
                                       hashlib.sha256).hexdigest()
        url = urljoin(BASE_URL, PATH)
        print(url)
        r = requests.get(url, headers=headers, params=params)
        dataSet = r.json()

        snapshots = dataSet['snapshotVos']

        concatenated_df = None
        for me_snapshot in snapshots:
            data_df = pd.DataFrame(me_snapshot['data']['assets'])
            data_df['updateTime'] = me_snapshot['updateTime']
            if concatenated_df is None:
                concatenated_df = data_df.copy()
            else:
                concatenated_df = pd.concat([concatenated_df, data_df])

        concatenated_df['date'] = pd.to_datetime(concatenated_df['updateTime'], unit='ms')
        concatenated_df['date'] = concatenated_df['date'] + timedelta(seconds=1)

        return concatenated_df

    def get_futures_balance_snapshot(self, request_date):
        request_date = request_date.replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = request_date
        end_time = request_date + timedelta(days=1)
        result_df = self.get_futures_balance_history(start_time, end_time)
        result_df = result_df[result_df['date'] == request_date]
        return result_df

    def get_futures_positions_margin_change_history(self, assets, start_time, end_time):
        positions_margin_change_df = None
        for asset in assets:
            if positions_margin_change_df is None:
                positions_margin_change_df = self.get_futures_position_margin_change_history(asset, start_time,
                                                                                             end_time)
            else:
                add_transfer_df = self.get_futures_position_margin_change_history(asset, start_time, end_time)
                if add_transfer_df is not None:
                    positions_margin_change_df = pd.concat([positions_margin_change_df, add_transfer_df])
        if positions_margin_change_df is not None:
            return positions_margin_change_df[['date', 'asset', 'amount']]
        return positions_margin_change_df




    def get_balance(self):
        # Recupérer la balance
        balance = self.exchange.fetchTotalBalance(params={})
        ticker_data = self.exchange.fetchTickers()
        usdt_balance = balance['USDT']
        ETH = float(ticker_data['ETH/USDT']['info']['lastPrice'])
        BTC = float(ticker_data['BTC/USDT']['info']['lastPrice'])
        LTC = float(ticker_data['LTC/USDT']['info']['lastPrice'])
        TRX = float(ticker_data['TRX/USDT']['info']['lastPrice'])
        XRP = float(ticker_data['XRP/USDT']['info']['lastPrice'])
        EOS = float(ticker_data['EOS/USDT']['info']['lastPrice'])
        BCH = float(ticker_data['BCH/USDT']['info']['lastPrice'])
        minBTC = 20 / BTC
        minETH = 20 / ETH
        minLTC = 20 / LTC
        minXRP = 20 / XRP
        minEOS = 20 / EOS
        minTRX = 20 / TRX
        minBCH = 20 / BCH
        return usdt_balance, balance, ticker_data, minBTC, minETH, minLTC, minXRP, minEOS, minTRX, minBCH

    def make_sure_positions_changed(self, positions, sleeping_time=45):
        position_changed = False
        counter = 1
        while not position_changed:
            if counter > 1:
                print(f'position not reached : reupdating positions {positions}')
            self.cancel_all_spot_open_orders()
            position_changed = self.change_position(positions)
            # Prints the current time with a five second difference
            print(f'waiting for the oder to be filled {sleeping_time}')
            time.sleep(sleeping_time)
            counter = counter + 1

    def update_position(self, pair, pair_signal):
        print(f'entering the global update position for {pair} and signals {pair_signal}')
        print('canceling all orders')
        positions = {}
        if pair == 'BTCUSDT':
            positions['BTC'] = pair_signal
            self.make_sure_positions_changed(positions)
        else:
            print(f'pair not handled for the moment {pair}')

    def change_position(self, positions):
        print(f'incoming positions to hodl {positions}')
        usdt_balance, balance, ticker_data, minBTC, minETH, minLTC, minXRP, minEOS, minTRX, minBCH = self.get_balance()
        ETH = float(ticker_data['ETH/USDT']['info']['lastPrice'])
        BTC = float(ticker_data['BTC/USDT']['info']['lastPrice'])
        LTC = float(ticker_data['LTC/USDT']['info']['lastPrice'])
        TRX = float(ticker_data['TRX/USDT']['info']['lastPrice'])
        XRP = float(ticker_data['XRP/USDT']['info']['lastPrice'])
        EOS = float(ticker_data['EOS/USDT']['info']['lastPrice'])
        BCH = float(ticker_data['BCH/USDT']['info']['lastPrice'])
        # calculer avec le last de binance!
        Tbtc = round(positions.get('BTC', 0) * balance['USDT'] / BTC, 4)
        Teth = round(positions.get('ETH', 0) * balance['USDT'] / ETH, 3)
        Teos = round(positions.get('EOS', 0) * balance['USDT'] / EOS, 3)
        Txrp = round(positions.get('XRP', 0) * balance['USDT'] / XRP, 0)
        Tltc = round(positions.get('LTC', 0) * balance['USDT'] / LTC, 2)
        Ttrx = round(positions.get('TRX', 0) * balance['USDT'] / TRX, 0)
        Tbch = round(positions.get('BCH', 0) * balance['USDT'] / BCH, 3)
        balance2 = self.exchange.fapiPrivate_get_positionrisk()
        PBTC, PETH, PLTC, PXRP, PTRX, PBCH, PEOS = 0, 0, 0, 0, 0, 0, 0
        for i in range(len(balance2)):
            if balance2[i]['symbol'] == 'BTCUSDT':
                PBTC = balance2[i]['positionAmt']
            elif balance2[i]['symbol'] == 'ETHUSDT':
                PETH = balance2[i]['positionAmt']
            elif balance2[i]['symbol'] == 'LTCUSDT':
                PLTC = balance2[i]['positionAmt']
            elif balance2[i]['symbol'] == 'XRPUSDT':
                PXRP = balance2[i]['positionAmt']
            elif balance2[i]['symbol'] == 'TRXUSDT':
                PTRX = balance2[i]['positionAmt']
            elif balance2[i]['symbol'] == 'EOSUSDT':
                PEOS = balance2[i]['positionAmt']
            elif balance2[i]['symbol'] == 'BCHUSDT':
                PBCH = balance2[i]['positionAmt']
        # trades à faire:
        Ebtc = - float(PBTC) if Tbtc == 0 else round(float(Tbtc) - float(PBTC), 4)
        Eeth = - float(PETH) if Teth == 0 else round(float(Teth) - float(PETH), 2)
        Eeos = - float(PEOS) if Teos == 0 else round(float(Teos) - float(PEOS), 2)
        Eltc = - float(PLTC) if Tltc == 0 else round(float(Tltc) - float(PLTC), 2)
        Exrp = - float(PXRP) if Txrp == 0 else round(float(Txrp) - float(PXRP), 0)
        Etrx = - float(PTRX) if Ttrx == 0 else round(float(Ttrx) - float(PTRX), 0)
        Ebch = - float(PBCH) if Tbch == 0 else round(float(Tbch) - float(PBCH), 0)

        position_threshold_reached = True
        if Ebtc > minBTC:
            print('current BTC position ' + str(PBTC))
            print('target BTC position ' + str(Tbtc))
            coursbtc = float(ticker_data['BTC/USDT']['info']['bidPrice']) - 1
            print('creating order buy at ' + str(coursbtc) + ' for amount ' + str(Ebtc))
            self.exchange.create_order(symbol='BTC/USDT', type='limit', side='buy', amount=Ebtc, price=coursbtc)
            position_threshold_reached = False
        elif Ebtc < -minBTC:
            print('current BTC position ' + str(PBTC))
            print('target BTC position ' + str(Tbtc))
            coursbtc = float(ticker_data['BTC/USDT']['info']['askPrice']) + 1
            print('creating order buy at ' + str(coursbtc) + ' for amount ' + str(Ebtc))
            self.exchange.create_order(symbol='BTC/USDT', type='limit', side='sell', amount=abs(Ebtc), price=coursbtc)
            position_threshold_reached = False

        if Eeth > minETH:
            courseth = float(ticker_data['ETH/USDT']['info']['bidPrice']) - 0.05
            self.exchange.create_order(symbol='ETH/USDT', type='limit', side='buy', amount=Eeth, price=courseth)
            position_threshold_reached = False
        elif Eeth < -minETH:
            courseth = float(ticker_data['ETH/USDT']['info']['askPrice']) + 0.05
            self.exchange.create_order(symbol='ETH/USDT', type='limit', side='sell', amount=abs(Eeth), price=courseth)
            position_threshold_reached = False

        if Eltc > minLTC:
            coursltc = float(ticker_data['LTC/USDT']['info']['bidPrice']) - 0.02
            self.exchange.create_order(symbol='LTC/USDT', type='limit', side='buy', amount=Eltc, price=coursltc)
            position_threshold_reached = False
        elif Eltc < -minLTC:
            coursltc = float(ticker_data['LTC/USDT']['info']['askPrice']) + 0.02
            self.exchange.create_order(symbol='LTC/USDT', type='limit', side='sell', amount=abs(Eltc), price=coursltc)
            position_threshold_reached = False

        if Exrp > minXRP:
            coursxrp = float(ticker_data['XRP/USDT']['info']['bidPrice']) - 0.0001
            self.exchange.create_order(symbol='XRP/USDT', type='limit', side='buy', amount=Exrp, price=coursxrp)
            position_threshold_reached = False
        elif Exrp < -minXRP:
            coursxrp = float(ticker_data['XRP/USDT']['info']['askPrice']) + 0.0001
            self.exchange.create_order(symbol='XRP/USDT', type='limit', side='sell', amount=abs(Exrp), price=coursxrp)
            position_threshold_reached = False

        if Eeos > minEOS:
            courseos = float(ticker_data['EOS/USDT']['info']['bidPrice'])
            self.exchange.create_order(symbol='EOS/USDT', type='limit', side='buy', amount=Eeos, price=courseos)
            position_threshold_reached = False
        elif Eeos < -minEOS:
            courseos = float(ticker_data['EOS/USDT']['info']['askPrice'])
            self.exchange.create_order(symbol='EOS/USDT', type='limit', side='sell', amount=abs(Eeos), price=courseos)
            position_threshold_reached = False

        if Etrx > minTRX:
            courstrx = float(ticker_data['TRX/USDT']['info']['bidPrice'])
            self.exchange.create_order(symbol='TRX/USDT', type='limit', side='buy', amount=Etrx, price=courstrx)
            position_threshold_reached = False
        elif Etrx < -minTRX:
            courstrx = float(ticker_data['TRX/USDT']['info']['askPrice'])
            self.exchange.create_order(symbol='TRX/USDT', type='limit', side='sell', amount=abs(Etrx), price=courstrx)
            position_threshold_reached = False

        if Ebch > minBCH:
            coursbch = float(ticker_data['BCH/USDT']['info']['bidPrice'])
            self.exchange.create_order(symbol='BCH/USDT', type='limit', side='buy', amount=Ebch, price=coursbch)
            position_threshold_reached = False
        elif Ebch < -minBCH:
            coursbch = float(ticker_data['BCH/USDT']['info']['askPrice'])
            self.exchange.create_order(symbol='BCH/USDT', type='limit', side='sell', amount=abs(Ebch), price=coursbch)
            position_threshold_reached = False
        return position_threshold_reached


