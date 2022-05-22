import time
from datetime import datetime

import pandas as pd

from Utils import DataHelpers


def getBalanceOut(data, single=False, futures=False):
    if not single:
        outData = []
        if not futures:
            for asset in data:
                coinData = {'asset': asset['coin'], 'free': asset['free'], 'locked': asset['locked'],
                            'exchangeSpecific': asset}
                outData.append(coinData)
            return outData
        else:
            for key, value in data.items():
                coinData = {'asset': key, 'free': value['available_balance'], 'locked': value['used_margin'],
                            'exchangeSpecific': value}
                outData.append(coinData)
            return outData
    else:
        if not futures:
            outData = {'asset': data['coin'], 'free': data['free'], 'locked': data['locked'], 'exchangeSpecific': data}
            return outData
        else:
            outData = {}
            key = list(data.keys())[0]

            outData['asset'] = key
            outData['free'] = data[key]['available_balance']
            outData['locked'] = data[key]['used_margin']
            outData['exchangeSpecific'] = data[key]
            return outData


def getMyTradeHistoryOut(data, futures=False):
    outData = []
    if futures:
        for history in data:
            outData.append(
                {'symbol': history['symbol'], 'id': history['exec_id'], 'orderId': history['order_id'],
                 'orderListId': history['order_link_id'], 'price': history['price'],
                 'qty': history['order_qty'],
                 'quoteQty': str(float(history['price']) * float(history['order_qty'])),
                 'commission': None, 'commissionAsset': None, 'time': history['trade_time_ms'],
                 'isBuyer': None, 'isMaker': None, 'isBestMatch': None, 'exchangeSpecific': history}
            )
    else:
        for history in data:
            outData.append(
                {'symbol': history['symbol'], 'id': history['id'], 'orderId': history['orderId'],
                 'orderListId': -1, 'price': history['price'], 'qty': history['qty'],
                 'quoteQty': str(float(history['price']) * float(history['qty'])),
                 'commission': history['commission'], 'commissionAsset': history['commissionAsset'],
                 'time': history['time'], 'isBuyer': history['isBuyer'], 'isMaker': history['isMaker'],
                 'isBestMatch': None, 'exchangeSpecific': history}
            )
    return outData


def getRecentTradeHistoryOut(data, futures=False):
    outData = []
    if futures:
        for datum in data:
            outData.append({
                'id': datum['id'], 'price': datum['price'], 'qty': datum['qty'],
                'quoteQty': str(float(datum['qty'] * datum['price'])),
                'time': datum['trade_time_ms'], 'isBuyerMaker': None, 'isBestMatch': None, 'exchangeSpecific': datum
            })
    else:
        for datum in data:
            outData.append({
                'id': None, 'price': datum['price'], 'qty': datum['qty'],
                'quoteQty': str(float(datum['qty']) * float(datum['price'])),
                'time': datum['time'], 'isBuyerMaker': datum['isBuyerMaker'], 'isBestMatch': None,
                'exchangeSpecific': datum
            })
    return outData


def getMakeSpotOrderOut(data):
    return {
        'symbol': data['symbol'],
        'orderId': data['orderId'],
        'orderListId': -1,
        'clientOrderId': data['orderLinkId'],
        'transactTime': data['transactTime'],
        'price': data['price'],
        'origQty': data['origQty'],
        'executedQty': data['executedQty'],
        'cummulativeQuoteQty': None,
        'status': data['status'],
        'timeInForce': data['timeInForce'],
        'type': data['type'],
        'side': data['side'],
        'fills': None,
        'exchangeSpecific': data
    }


def getOrderOut(data, futures=False):
    if futures:
        pass
    else:
        return {
            'symbol': data['symbol'],
            'orderId': data['orderId'],
            'orderListId': -1,
            'clientOrderId': data['orderLinkId'],
            'price': data['price'],
            'origQty': data['origQty'],
            'executedQty': data['executedQty'],
            'cummulativeQuoteQty': data['cummulativeQuoteQty'],
            'status': data['status'],
            'timeInForce': data['timeInForce'],
            'type': data['type'],
            'side': data['side'],
            'stopPrice': data['stopPrice'],
            'icebergQty': data['icebergQty'],
            'time': data['time'],
            'updateTime': data['updateTime'],
            'isWorking': data['isWorking'],
            'origQuoteOrderQty': None,
            'exchangeSpecific': data
        }


def getOpenOrdersOut(data, futures=False):
    outData = []
    if futures:
        pass
    else:
        for datum in data:
            outData.append({
                'symbol': datum['symbol'],
                'orderId': datum['orderId'],
                'orderListId': None,
                'clientOrderId': datum['orderLinkId'],
                'price': datum['price'],
                'origQty': datum['origQty'],
                'executedQty': datum['executedQty'],
                'cummulativeQuoteQty': datum['cummulativeQuoteQty'],
                'status': datum['status'],
                'timeInForce': datum['timeInForce'],
                'type': datum['type'],
                'side': datum['side'],
                'stopPrice': datum['stopPrice'],
                'icebergQty': datum['icebergQty'],
                'time': datum['time'],
                'updateTime': datum['updateTime'],
                'isWorking': datum['isWorking'],
                'origQuoteOrderQty': None,
                'exchangeSpecific': datum
            })
    return outData


def futuresOrderOut(data, isConditional=False):
    if isConditional:
        return {
            'symbol': data['symbol'],
            'orderId': data['stop_order_id'],
            'clientOrderId': data['order_link_id'],
            'transactTime': time.mktime(
                datetime.strptime(data['created_time'], '%Y-%m-%dT%H:%M:%SZ').timetuple()),
            'price': data['price'],
            'origQty': data['qty'],
            'executedQty': 0.0,
            'cummulativeQuoteQty': 0.0,
            'status': data['order_status'],
            'timeInForce': data['time_in_force'],
            'type': data['order_type'],
            'side': data['side'],
            'extraData': {
                'reduceOnly': data['reduce_only'],
                'stopPrice': data['trigger_price'],
                'workingType': data['trigger_by'],
                'avgPrice': 0.0,
                'origType': data['order_type'],
                'positionSide': None,
                'activatePrice': None,
                'priceRate': None,
                'closePosition': data['close_on_trigger'],
            },
            'exchangeSpecific': data
        }
    else:
        return {
            'symbol': data['symbol'],
            'orderId': data['order_id'],
            'clientOrderId': data['order_link_id'],
            'transactTime': time.mktime(
                datetime.strptime(data['created_time'], '%Y-%m-%dT%H:%M:%SZ').timetuple()),
            'price': data['price'],
            'origQty': data['qty'],
            'executedQty': data['cum_exec_qty'],
            'cummulativeQuoteQty': data['cum_exec_value'],
            'status': data['order_status'],
            'timeInForce': data['time_in_force'],
            'type': data['order_type'],
            'side': data['side'],
            'extraData': {
                'reduceOnly': data['reduce_only'],
                'stopPrice': 0.0,
                'workingType': None,
                'avgPrice': 0.0,
                'origType': data['order_type'],
                'positionSide': None,
                'activatePrice': None,
                'priceRate': None,
                'closePosition': data['close_on_trigger'],
            },
            'exchangeSpecific': data
        }


def makeDummyBalance(asset):
    return {
        'asset': asset,
        'free': str(0.0),
        'locked': str(0.0),
        'exchangeSpecific': {}
    }


def getSpotOrderAsDict(order: DataHelpers.OrderData):
    params = {
        'symbol': order.symbol,
        'qty': order.quantity,
        'side': order.side,
        'type': order.orderType,
        'timeInForce': order.timeInForce,
        'price': order.price,
        'orderLinkId': order.newClientOrderId
    }
    return params


def getFuturesOrderAsDict(order: DataHelpers.futuresOrderData, timeInForceTranslate):
    if 'STOP' in order.orderType:
        params = {
            'side': order.side.lower().title(),
            'symbol': order.symbol,
            'order_type': 'Market' if order.orderType == 'STOP_MARKET' else 'Limit',
            'qty': order.quantity,
            'price': order.price,
            'base_price': order.extraParams['basePrice'],
            'stop_px': order.stopPrice,

            'time_in_force': order.timeInForce if order.timeInForce in timeInForceTranslate.values()
            else timeInForceTranslate[order.timeInForce],

            'close_on_trigger': order.closePosition,
            'reduce_only': order.reduceOnly
        }

        if 'triggerBy' in order.extraParams.keys():
            params['trigger_by'] = order.extraParams['triggerBy']

    else:
        params = {
            'side': order.side.lower().title(),
            'symbol': order.symbol,
            'order_type': order.orderType.lower().title(),
            'qty': order.quantity,

            'time_in_force': order.timeInForce if order.timeInForce in timeInForceTranslate.values()
            else timeInForceTranslate[order.timeInForce],

            'close_on_trigger': order.closePosition,
            'reduce_only': order.reduceOnly
        }

    if order.price is not None:
        params['price'] = order.price

    if order.newClientOrderId is not None:
        params['order_link_id'] = order.newClientOrderId

    if 'takeProfit' in order.extraParams.keys():
        params['take_profit'] = order.extraParams['takeProfit']

    if 'stopLoss' in order.extraParams.keys():
        params['stop_loss'] = order.extraParams['stopLoss']

    if 'tpTriggerBy' in order.extraParams.keys():
        params['tp_trigger_by'] = order.extraParams['tpTriggerBy']

    if 'slTriggerBy' in order.extraParams.keys():
        params['sl_trigger_by'] = order.extraParams['slTriggerBy']

    if 'positionIdx' in order.extraParams.keys():
        params['position_idx'] = order.extraParams['positionIdx']

    return params


def convertIntervalToFuturesKlines(interval):
    if interval == '1m':
        return 1
    elif interval == '3m':
        return 3
    elif interval == '5m':
        return 5
    elif interval == '15m':
        return 15
    elif interval == '30m':
        return 30
    elif interval == '1h':
        return 60
    elif interval == '2h':
        return 120
    elif interval == '4h':
        return 240
    elif interval == '6h':
        return 360
    elif interval == '12h':
        return 720
    elif interval == '1d':
        return 'D'
    elif interval == '1w':
        return 'W'
    elif interval == '1M':
        return 'M'


def getIntervalInSeconds(interval, validIntervals):
    if interval not in validIntervals:
        raise ValueError('Incorrect time interval specified')
    if interval == '1m':
        return 60
    elif interval == '3m':
        return 3 * 60
    elif interval == '5m':
        return 5 * 60
    elif interval == '15m':
        return 15 * 60
    elif interval == '30m':
        return 30 * 60
    elif interval == '1h':
        return 60 * 60
    elif interval == '2h':
        return 120 * 60
    elif interval == '4h':
        return 240 * 60
    elif interval == '6h':
        return 360 * 60
    elif interval == '12h':
        return 720 * 60
    elif interval == '1d':
        return 86400
    elif interval == '1w':
        return 7 * 86400
    elif interval == '1M':
        return 30 * 86400


def getKlinesDesiredOnlyCols(data, desiredIndexes):
    finalDataArray = []
    for datum in data:
        finalDataArray.append([datum[index] for index in desiredIndexes])
    return finalDataArray


def klinesConvertToPandas(finalDataArray):
    df = pd.DataFrame(finalDataArray,
                      columns=['date', 'open', 'high', 'low', 'close', 'volume', 'closeDate', 'tradesNum'])
    df.set_index('date', inplace=True)
    return df


def klinesConvertDate(data, futures, timeColIdxs):
    for datum in data:
        for idx in timeColIdxs:
            if futures:
                datum[idx] = datetime.fromtimestamp(float(datum[idx]))
            else:
                datum[idx] = datetime.fromtimestamp(float(datum[idx]) / 1000)
