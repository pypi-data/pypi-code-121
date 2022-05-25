"""
To see which endpoints and topics are available, check the Bybit API 
documentation: https://bybit-exchange.github.io/docs/inverse/#t-websocket

There are several WSS URLs offered by Bybit, which pybit manages for you.
However, you can set a custom `domain` as shown below.
"""

from time import sleep

# Import your desired markets from pybit
from pybit import usdc_options
from pybit import spot

"""
An alternative way to import:
from pybit.inverse_perpetual import WebSocket, HTTP
"""

# Set up logging (optional)
import logging
logging.basicConfig(filename="pybit.log", level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")

# testnet
api_key = "RdHxmhZAaqqFn3aI19"
api_secret = "XCgnXkuRGwrk6NdWIGt0SNmC1nr671UsZfaS"
# mainnet
#api_key = "oo41mOmCWs4FLbt5o8"
#api_secret = "szj59aOiHAqMljDKyy14TEt4tdyfzGcG5fCL"

# Connect with authentication!
ws = usdc_options.WebSocket(
    test=True,
    api_key=api_key,  # omit the api_key & secret to connect w/o authentication
    api_secret=api_secret,
    # to pass a custom domain in case of connectivity problems, you can use:
    #domain="bytick"  # the default is "bybit"
    trace_logging=True,
)

# Let's fetch the orderbook for BTCUSD. First, we'll define a function.
def handle_orderbook(message):
    # I will be called every time there is new orderbook data!
    print(message)
    orderbook_data = message["data"]

# Now, we can subscribe to the orderbook stream and pass our arguments:
# our function and our selected symbol.
# To subscribe to multiple symbols, pass a list: ["BTCUSD", "ETHUSD"]
# To subscribe to all symbols, pass "*".
ws.delta_orderbook_100_stream(handle_orderbook, "BTC-13MAY22-25000-C")
#ws.custom_topic_stream("wss://{SUBDOMAIN}.{DOMAIN}.com/trade/option/usdc/public/v1",
#                       "delta.orderbook100.BTC-13MAY22-25000-C", handle_orderbook)

#"""
# To subscribe to private data, the process is the same:
def handle_position(message):
    # I will be called every time there is new position data!
    print(message)

ws.position_stream(handle_position)
ws.execution_stream(handle_position)
ws.order_stream(handle_position)
#ws.custom_topic_stream("wss://{SUBDOMAIN}.{DOMAIN}.com/trade/option/usdc/private/v1",
#                       "user.openapi.option.position", handle_position)
#"""

while True:
    # This while loop is required for the program to run. You may execute
    # additional code for your trading logic here.
    sleep(1)
