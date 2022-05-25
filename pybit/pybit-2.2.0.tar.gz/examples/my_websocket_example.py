"""
To see which endpoints and topics are available, check the Bybit API
documentation: https://bybit-exchange.github.io/docs/inverse/#t-websocket

There are several WSS URLs offered by Bybit, which pybit manages for you.
However, you can set a custom `domain` as shown below.
"""

from time import sleep

# Import your desired markets from pybit
from pybit import usdc_perpetual, usdt_perpetual, inverse_perpetual, spot

"""
An alternative way to import:
from pybit.inverse_perpetual import WebSocket, HTTP
"""

# Set up logging (optional)
import logging
logging.basicConfig(filename="pybit.log", level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")

api_key = "yrusSyuhtwc8zHAqfA"
api_secret = "QHcfc4YwvA2zzqXJBKu7FNz5uK55PmhhVQfH"

# Connect with authentication!
ws = usdc_perpetual.WebSocket(
    test=False,
    api_key=api_key,  # omit the api_key & secret to connect w/o authentication
    api_secret=api_secret,
    # to pass a custom domain in case of connectivity problems, you can use:
    #domain="bytick",  # the default is "bybit"
    trace_logging=True,
)

def handle_orderbook(message):
    print(message)
    #orderbook_data = message["data"]
    #print(len(orderbook_data))

def h1(message):
    print(1, message)
def h2(message):
    print(2, message)
def h3(message):
    print(3, message)

ws.order_stream(h1)
ws.execution_stream(h2)
ws.position_stream(h3)

#ws.custom_topic_stream("wss://stream.bybit.com/perpetual/ws/v1/realtime_public",
#                       "orderBookL2_25.BTCPERP", handle_orderbook)

#ws.trade_stream(handle_orderbook, "BTCPERP")

#ws.trade_v1_stream(handle_orderbook, "BTCUSDT")
#ws.trade_v2_stream(handle_orderbook, "BTCUSDT")
#ws.outbound_account_info_stream(handle_orderbook)
#ws.position_stream(handle_orderbook)
#ws.order_stream(handle_orderbook)

while True:
    # Run your main trading logic here.
    sleep(1)
