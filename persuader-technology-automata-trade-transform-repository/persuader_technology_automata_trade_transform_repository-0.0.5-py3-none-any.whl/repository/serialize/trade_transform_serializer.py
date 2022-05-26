from tradetransformrepo.TradeTransform import TradeTransform


def serialize_trade_transform(trade_transform: TradeTransform) -> dict:
    serialized = {
        'trade': trade_transform.trade
    }
    if trade_transform.transform is not None:
        serialized['transform'] = trade_transform.transform
    return serialized
