from core.number.BigFloat import BigFloat
from core.trade.InstrumentTrade import InstrumentTrade, Status, TradeMode
from coreutility.collection.dictionary_utility import as_data
from coreutility.string.string_utility import is_empty


def deserialize_trade(trade) -> InstrumentTrade:
    if trade is not None:
        instrument_from = as_data(trade, 'instrument_from')
        instrument_to = as_data(trade, 'instrument_to')
        quantity = BigFloat(as_data(trade, 'quantity'))
        price = as_data(trade, 'price')
        value = as_data(trade, 'value')
        status = as_data(trade, 'status')
        description = as_data(trade, 'description')
        order_id = as_data(trade, 'order_id')
        instant = as_data(trade, 'instant')
        mode = as_data(trade, 'mode')
        deserialized_trade = InstrumentTrade(instrument_from, instrument_to, quantity)
        set_price_as_available(deserialized_trade, price)
        set_value_as_available(deserialized_trade, value)
        set_status_as_available(deserialized_trade, status)
        set_mode_as_available(deserialized_trade, mode)
        set_description_as_available(deserialized_trade, description)
        set_orderid_as_available(deserialized_trade, order_id)
        set_instant_as_available(deserialized_trade, instant)
        return deserialized_trade


def set_price_as_available(deserialized_trade, value):
    if not is_empty(value):
        deserialized_trade.price = BigFloat(value)


def set_value_as_available(deserialized_trade, value):
    if not is_empty(value):
        deserialized_trade.value = BigFloat(value)


def set_status_as_available(deserialized_trade, value):
    if value is not None:
        deserialized_trade.status = Status.parse(value)


def set_description_as_available(deserialized_trade, value):
    if not is_empty(value):
        deserialized_trade.description = value


def set_orderid_as_available(deserialized_trade, value):
    if not is_empty(value):
        deserialized_trade.order_id = value


def set_instant_as_available(deserialized_trade, value):
    if value is not None:
        deserialized_trade.instant = value


def set_mode_as_available(deserialized_trade, value):
    if value is not None:
        deserialized_trade.mode = TradeMode.parse(value)
