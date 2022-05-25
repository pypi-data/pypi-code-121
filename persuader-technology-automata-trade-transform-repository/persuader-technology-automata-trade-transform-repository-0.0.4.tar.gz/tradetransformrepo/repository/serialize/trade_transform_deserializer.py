from coreutility.collection.dictionary_utility import as_data

from tradetransformrepo.TradeTransform import TradeTransform


def deserialize_trade_transform(trade_transform) -> TradeTransform:
    if trade_transform is not None:
        trade = as_data(trade_transform, 'trade')
        transform = as_data(trade_transform, 'transform')
        deserialized = TradeTransform(trade, transform)
        return deserialized
