#!/usr/bin/env python3
# coding: utf-8

import ccxt
import urllib.parse,  urllib.request
from urllib.parse import urljoin, urlencode
import json, hashlib, hmac, time
from datetime import datetime
import requests
import calendar

import pandas as pd
import numpy as np

from datetime import  timedelta

from binance.client import Client

class BinanceFutureBot(object):

    def __init__(self, BINANCE_PUBLIC, BINANCE_PRIVATE):

        client = Client(BINANCE_PUBLIC, BINANCE_PRIVATE)
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

    def cancel_all_order(self, pair):
        Cleaner = self.exchange.fetch_open_orders(pair)
        L = len(Cleaner)
        if L > 0:
            for i in range(0, L):
                self.exchange.cancel_order(Cleaner[i]['info']['orderId'], 'BTC/USDT')

    def cancel_all_orders(self):
        self.cancel_all_order('BTC/USDT')
        self.cancel_all_order('ETH/USDT')
        self.cancel_all_order('LTC/USDT')
        self.cancel_all_order('EOS/USDT')
        self.cancel_all_order('XRP/USDT')
        self.cancel_all_order('BCH/USDT')
        self.cancel_all_order('TRX/USDT')


    def get_spot_universe(self):

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
            'limit':300

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
            else :
                concatenated_df = pd.concat([concatenated_df, data_df])

        concatenated_df['date'] = pd.to_datetime(concatenated_df['updateTime'], unit='ms')
        concatenated_df['date'] = concatenated_df['date'] + timedelta(seconds=1)

        return concatenated_df


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
            'limit':300

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
            else :
                concatenated_df = pd.concat([concatenated_df, data_df])

        concatenated_df['date'] = pd.to_datetime(concatenated_df['updateTime'], unit='ms')
        concatenated_df['date'] = concatenated_df['date'] + timedelta(seconds=1)

        return concatenated_df



    def get_futures_balance_snapshot(self, request_date):
        request_date = request_date.replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = request_date
        end_time = request_date + timedelta(days = 1)
        result_df = self.get_futures_balance_history(start_time, end_time)
        result_df = result_df[result_df['date'] == request_date]
        return result_df

    def get_futures_positions_margin_change_history(self, assets, start_time, end_time):
        positions_margin_change_df = None
        for asset in assets:
            if positions_margin_change_df is None:
                positions_margin_change_df = self.get_futures_position_margin_change_history(asset, start_time, end_time)
            else:
                add_transfer_df = self.get_futures_position_margin_change_history(asset, start_time, end_time)
                if add_transfer_df is not None:
                    positions_margin_change_df = pd.concat([positions_margin_change_df, add_transfer_df])
        if positions_margin_change_df is not None:
            return positions_margin_change_df[['date','asset','amount']]
        return positions_margin_change_df

    def get_futures_position_margin_change_history(self, asset, start_time, end_time):

        startTime = int(start_time.timestamp() * 1000)
        endTime = int(end_time.timestamp() * 1000)

        BASE_URL = 'https://fapi.binance.com'
        PATH = '/fapi/v1/positionMargin/history'


        headers = {
            'X-MBX-APIKEY': self.apiKey
        }
        timestamp = int(time.time() * 1000)

        params = {
            'symbol': asset,
            'type' : 1,
            'recvWindow': 60000,
            'timestamp': timestamp,
            'startTime': startTime,
            'endTime': endTime,
##            'limit': 500,
##           'type':2
        }
        query_string = urllib.parse.urlencode(params)
        params['signature'] = hmac.new(self.secret.encode('utf-8'), query_string.encode('utf-8'),
                                       hashlib.sha256).hexdigest()
        url = urljoin(BASE_URL, PATH)
        print(url)
        r = requests.get(url, headers=headers, params=params)
        dataSet = r.json()
        if dataSet['total']>0:
            transfers = dataSet['rows']

            transfer_df = pd.DataFrame(transfers)

            transfer_df['date'] = pd.to_datetime(transfer_df['timestamp'], unit='ms')

            return transfer_df
        else :
            return None



    def get_future_position_risk(self):


        BASE_URL = 'https://fapi.binance.com'
        PATH = '/fapi/v2/positionRisk'


        headers = {
            'X-MBX-APIKEY': self.apiKey
        }
        timestamp = int(time.time() * 1000)

        params = {
            'recvWindow': 60000,
            'timestamp': timestamp,
        }
        query_string = urllib.parse.urlencode(params)
        params['signature'] = hmac.new(self.secret.encode('utf-8'), query_string.encode('utf-8'),
                                       hashlib.sha256).hexdigest()
        url = urljoin(BASE_URL, PATH)
        print(url)
        r = requests.get(url, headers=headers, params=params)
        dataSet = r.json()
        return dataSet

    def get_futures_transfer_history(self, assets, start_time, end_time):
        transfer_df = None
        for asset in assets:
            if transfer_df is None:
                transfer_df = self.get_coin_futures_transfer_history(asset, start_time, end_time)
            else:
                add_transfer_df = self.get_coin_futures_transfer_history(asset, start_time, end_time)
                if add_transfer_df is not None:
                    transfer_df = pd.concat([transfer_df, add_transfer_df])
        if transfer_df is not None:
            return transfer_df[['date','asset','amount','type']]
        return transfer_df

    def get_top_trader_long_short_ration(self,  asset, start_time, end_time, period):

        startTime = int(start_time.timestamp() * 1000)
        endTime = int(end_time.timestamp() * 1000)

        BASE_URL = 'https://fapi.binance.com'
        PATH = '/futures/data/topLongShortPositionRatio'


        headers = {
            'X-MBX-APIKEY': self.apiKey
        }

        params = {
            'symbol': asset,
            'period': period,
            'startTime': startTime,
            'endTime': endTime,
            'limit':30

        }
        query_string = urllib.parse.urlencode(params)
        params['signature'] = hmac.new(self.secret.encode('utf-8'), query_string.encode('utf-8'),
                                       hashlib.sha256).hexdigest()
        url = urljoin(BASE_URL, PATH)
        print(url)
        r = requests.get(url, headers=headers, params=params)
        dataSet = r.json()
        ls_ratio_df = pd.DataFrame(dataSet)
        ls_ratio_df.index = pd.to_datetime(ls_ratio_df['timestamp'], unit='ms')

        return ls_ratio_df

    def get_coin_futures_transfer_history(self, asset, start_time, end_time):

        startTime = int(start_time.timestamp() * 1000)
        endTime = int(end_time.timestamp() * 1000)

        BASE_URL = 'https://api.binance.com'
        PATH = '/sapi/v1/futures/transfer'


        headers = {
            'X-MBX-APIKEY': self.apiKey
        }
        timestamp = int(time.time() * 1000)

        params = {
            'asset': asset,
            'recvWindow': 60000,
            'timestamp': timestamp,
            'startTime': startTime,
            'endTime': endTime,
            'limit':30

        }
        query_string = urllib.parse.urlencode(params)
        params['signature'] = hmac.new(self.secret.encode('utf-8'), query_string.encode('utf-8'),
                                       hashlib.sha256).hexdigest()
        url = urljoin(BASE_URL, PATH)
        print(url)
        r = requests.get(url, headers=headers, params=params)
        dataSet = r.json()
        if dataSet['total']>0:
            transfers = dataSet['rows']
            transfer_df = pd.DataFrame(transfers)

            transfer_df['date'] = pd.to_datetime(transfer_df['timestamp'], unit='ms')

            return transfer_df
        else :
            return None


    def get_balance_low_level(self, request_date):
        BASE_URL = 'https://api.binance.com'
        PATH = '/api/v3/account'
        if request_date is None:
            timestamp = int(time.time() * 1000)
        else:
            timestamp = calendar.timegm(request_date.timetuple())

        headers = {
            'X-MBX-APIKEY': self.apiKey
        }
        params = {
            'recvWindow': 5000,
            'timestamp': timestamp,
        }
        query_string = urllib.parse.urlencode(params)
        params['signature'] = hmac.new(self.secret.encode('utf-8'), query_string.encode('utf-8'),
                                       hashlib.sha256).hexdigest()
        url = urljoin(BASE_URL, PATH)
        print(url)
        r = requests.get(url, headers=headers, params=params)
        dataSet = r.json()
        print(dataSet)



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


    def make_sure_spot_positions_changed(self,positions, sleeping_time = 45):
        position_changed = False
        counter = 1
        while not  position_changed:
            if counter>1:
                print(f'position not reached : reupdating positions {positions}')
            self.cancel_all_orders()
            position_changed = self.change_position(positions)
            # Prints the current time with a five second difference
            print(f'waiting for the oder to be filled {sleeping_time}')
            time.sleep(sleeping_time)
            counter = counter+1


    def make_sure_positions_changed(self, positions, sleeping_time = 45):
        position_changed = False
        counter = 1
        while not  position_changed:
            if counter>1:
                print(f'position not reached : reupdating positions {positions}')
            self.cancel_all_orders()
            position_changed = self.change_position(positions)
            # Prints the current time with a five second difference
            print(f'waiting for the oder to be filled {sleeping_time}')
            time.sleep(sleeping_time)
            counter = counter+1

    def update_position(self, pair, pair_signal):
        print(f'entering the global update position for {pair} and signals {pair_signal}')
        print('canceling all orders')
        positions ={}
        if pair == 'BTCUSDT':
            positions['BTC']=pair_signal
            self.make_sure_positions_changed(positions)
        else :
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
        Tbtc = round(positions.get('BTC',0) * balance['USDT'] / BTC, 4)
        Teth = round(positions.get('ETH',0) * balance['USDT'] / ETH, 3)
        Teos = round(positions.get('EOS',0) * balance['USDT'] / EOS, 3)
        Txrp = round(positions.get('XRP',0) * balance['USDT'] / XRP, 0)
        Tltc = round(positions.get('LTC',0) * balance['USDT'] / LTC, 2)
        Ttrx = round(positions.get('TRX',0) * balance['USDT'] / TRX, 0)
        Tbch = round(positions.get('BCH',0) * balance['USDT'] / BCH, 3)
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
            print('current BTC position '+str(PBTC))
            print('target BTC position ' + str(Tbtc))
            coursbtc = float(ticker_data['BTC/USDT']['info']['bidPrice']) - 1
            print('creating order buy at '+str(coursbtc) + ' for amount '+str(Ebtc))
            self.exchange.create_order(symbol='BTC/USDT', type='limit', side='buy', amount=Ebtc, price=coursbtc)
            position_threshold_reached = False
        elif Ebtc < -minBTC:
            print('current BTC position '+str(PBTC))
            print('target BTC position ' + str(Tbtc))
            coursbtc = float(ticker_data['BTC/USDT']['info']['askPrice']) + 1
            print('creating order buy at '+str(coursbtc) + ' for amount '+str(Ebtc))
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


