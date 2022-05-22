def unifyGetBalanceSpotOut(data, isSingle=False):
    allAssets = []

    for asset in data:
        assetIndex = getAssetIndexInList(asset['currency'], allAssets)
        if assetIndex == -1:
            assetInfo = newEmptyAsset(asset['currency'])
        else:
            assetInfo = allAssets[assetIndex]

        assetInfo['free'] += float(asset['available'])
        assetInfo['locked'] += float(asset['holds'])
        assetInfo['exchangeSpecific'].append(asset)

        if assetIndex == -1:
            allAssets.append(assetInfo)

    if isSingle:
        return allAssets[0]
    else:
        return allAssets


def newEmptyAsset(assetName):
    return {
        'asset': assetName,
        'free': 0.0,
        'locked': 0.0,
        'exchangeSpecific': []
    }


def getAssetIndexInList(assetName, allAssets):
    for i in range(len(allAssets)):
        if assetName == allAssets[i]['asset']:
            return i
    return -1


def unifyTradeHistory(tradeHistory, futures=False):
    unifiedTradeHistory = []

    if futures:
        pass
    else:
        for trade in tradeHistory:
            isBuyer = True if trade['liquidity'] == 'taker' else False
            isMaker = True if trade['liquidity'] == 'maker' else False
            unifiedTradeHistory.append({
                'symbol': trade['symbol'],
                'id': trade['tradeId'],
                'orderId': trade['orderId'],
                'orderListId': -1,
                'price': trade['price'],
                'qty': trade['size'],
                'quoteQty': trade['funds'],
                'commission': trade['fee'],
                'commissionAsset': trade['feeCurrency'],
                'time': trade['createdAt'],
                'isBuyer': isBuyer,
                'isMaker': isMaker,
                'isBestMatch': None,
                'exchangeSpecific': trade
            })
        return unifiedTradeHistory


def unifyRecentTrades(tradeHistory, futures=False):
    unifiedTradeHistory = []

    if futures:
        for trade in tradeHistory:
            unifiedTradeHistory.append({
                'id': int(trade['sequence']),
                'price': float(trade['price']),
                'qty': float(trade['size']),
                'quoteQty': float(trade['price']) * float(trade['size']),
                'time': int(trade['ts'] / 1000),
                'isBuyerMaker': None,
                'exchangeSpecific': trade
            })
    else:
        for trade in tradeHistory:
            unifiedTradeHistory.append({
                'id': int(trade['sequence']),
                'price': float(trade['price']),
                'qty': float(trade['size']),
                'quoteQty': float(trade['price']) * float(trade['size']),
                'time': int(trade['time'] / 1000),
                'isBuyerMaker': None,
                'isBestMatch': None,
                'exchangeSpecific': trade
            })

    return unifiedTradeHistory
