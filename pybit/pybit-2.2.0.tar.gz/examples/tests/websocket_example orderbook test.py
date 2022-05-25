"""
To see which endpoints and topics are available, check the Bybit API 
documentation: https://bybit-exchange.github.io/docs/inverse/#t-websocket

There are several WSS URLs offered by Bybit, which pybit manages for you.
However, you can set a custom `domain` as shown below.
"""

from time import sleep

# Import your desired markets from pybit
from pybit import inverse_perpetual, usdt_perpetual, spot, usdc_perpetual

"""
An alternative way to import:
from pybit.inverse_perpetual import WebSocket, HTTP
"""

# Set up logging (optional)
import logging
logging.basicConfig(filename="pybit.log", level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")


# Connect with authentication!
ws_inverse = inverse_perpetual.WebSocket(
    test=True,
)
ws_usdt = usdt_perpetual.WebSocket(
    test=True,
)
ws_spot = spot.WebSocket(
    test=True,
)
ws_usdc = usdc_perpetual.WebSocket(
    test=True,
)

# Let's fetch the orderbook for BTCUSD. First, we'll define a function.
def handle_orderbook(message):
    # I will be called every time there is new orderbook data!
    print(message["topic"])
    #print(message)
    orderbook_data = message["data"]

# Now, we can subscribe to the orderbook stream and pass our arguments:
# our function and our selected symbol.
# To subscribe to multiple symbols, pass a list: ["BTCUSD", "ETHUSD"]
# To subscribe to all symbols, pass "*".

ws_inverse.orderbook_25_stream(handle_orderbook, "BTCUSD")
ws_inverse.orderbook_200_stream(handle_orderbook, "BTCUSD")
ws_usdt.orderbook_25_stream(handle_orderbook, "BTCUSDT")
ws_usdt.orderbook_200_stream(handle_orderbook, "BTCUSDT")
ws_spot.diff_depth_v1_stream(handle_orderbook, "BTCUSDT")
ws_spot.merged_depth_v1_stream(handle_orderbook, "BTCUSDT", 1)
ws_spot.depth_v1_stream(handle_orderbook, "BTCUSDT")
ws_spot.depth_v2_stream(handle_orderbook, "BTCUSDT")
ws_usdc.orderbook_25_stream(handle_orderbook, "BTCPERP")
ws_usdc.orderbook_200_stream(handle_orderbook, "BTCPERP")


while True:
    # This while loop is required for the program to run. You may execute
    # additional code for your trading logic here.
    sleep(1)
