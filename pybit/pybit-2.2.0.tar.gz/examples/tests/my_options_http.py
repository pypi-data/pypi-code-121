
# Import pybit and define the HTTP object.
from pybit import HTTP  # supports inverse perp & futures, usdt perp, spot.
"""
Some methods might need extra arguments due to the current Bybit APIs - 
which are divided across market types. To ensure you're sending requests to 
a specific market type, like Inverse Perpetual, you can import and define 
HTTP like so:

from pybit.inverse_perpetual import HTTP   <-- exclusively supports spot.
"""
from pybit import usdc_options  # <-- import HTTP & WSS for inverse perp
from pybit import spot  # <-- import HTTP & WSS for spot
from pybit import inverse_futures, usdt_perpetual

"""
You can create an authenticated or unauthenticated HTTP session. 
You can skip authentication by not passing any value for the key and secret.
"""

import logging
logging.basicConfig(filename="my_options_http.log", level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")

# testnet
api_key = "RdHxmhZAaqqFn3aI19"
api_secret = "XCgnXkuRGwrk6NdWIGt0SNmC1nr671UsZfaS"

# testnet MMP enabled account
#api_key = "d64312KxuBl25iNrqa"
#api_secret = "CrS5KH6bDsfxrrqVQIBpYySy8UsJ7MiS5AR8"


## Authenticated
session = usdc_options.HTTP(
    endpoint="https://api-testnet.bybit.com",
    api_key=api_key,
    api_secret=api_secret
)
from time import time
symbol = "BTC-29JUL22-10000-C"
orderLinkId = str(int(time()))
order = {"symbol": symbol, "orderType": "Limit", "side": "Buy", "orderPrice": "20000", "orderQty": "0.01", "timeInForce": "GoodTillCancel", "orderLinkId": orderLinkId}


def prepare_batch_request(batch_place_response, replace=False):
    batch_replace_request = []
    for order in batch_place_response["result"]:
        replace_order = {"symbol": order["symbol"],
                         "orderId": order["orderId"]}
        if replace:
            replace_order["orderPrice"] = "10000"
        batch_replace_request.append(replace_order)
    return batch_replace_request


#print(session.orderbook(symbol=symbol))
#print(session.query_symbol(symbol=symbol))
#print(session.latest_information_for_symbol(symbol=symbol))
#print(session.delivery_price())
#print(session.last_500_trades(category="OPTION"))
#
#r = session.place_active_order(**order)
#print(r)
#order_id = r["result"]["orderId"]
#
#r = session.batch_place_active_orders([order, order, order, order])
#print(r)
#batch_cancel_orders = prepare_batch_request(r)
#batch_replace_orders = prepare_batch_request(r, replace=True)
#
#print(session.get_active_order(category="OPTION"))
#print(session.cancel_active_order(symbol=symbol, orderId=order_id))
#print(session.batch_cancel_active_order(batch_cancel_orders))
#print(session.cancel_all_active_orders(symbol=symbol))
#print(session.replace_active_order(symbol=symbol, orderId=order_id, orderPrice="5000"))
#print(session.batch_replace_active_orders(batch_replace_orders))
print(session.user_trade_records(category="OPTION", startTime="1651588652000", limit="1"))
print(session.get_history_order(category="OPTION"))
print(session.wallet_fund_records(symbol=symbol))
print(session.get_wallet_balance())
print(session.get_asset_info(symbol=symbol))
print(session.get_margin_mode(symbol=symbol))
print(session.my_position(category="OPTION"))
print(session.query_delivery_history(symbol=symbol))
print(session.query_position_expiration_date())
#print(session.query_mmp(baseCoin="BTC"))
#print(session.modify_mmp(currency="BTC",windowMs=500000,frozenPeriodMs=300,qtyLimit="10",deltaLimit="100"))
#print(session.reset_mmp(currency="BTC"))
print()
"""
| Endpoint | Method |
| -------- | ------ |
|          |    `query_mmp`()    |
|          |    `modify_mmp`()    |
|          |    `reset_mmp`()    |"""

exit()
