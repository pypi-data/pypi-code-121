"""
To see which endpoints and topics are available, check the Bybit API 
documentation: https://bybit-exchange.github.io/docs/inverse/#t-websocket

There are several WSS URLs offered by Bybit, which pybit manages for you.
However, you can set a custom `domain` as shown below.
"""

from time import sleep

# Import your desired markets from pybit
from pybit import usdc_perpetual
from pybit import spot

"""
An alternative way to import:
from pybit.inverse_perpetual import WebSocket, HTTP
"""

# Set up logging (optional)
import logging
logging.basicConfig(filename="pybit.log", level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")


# Connect with authentication!
ws = usdc_perpetual.WebSocket(
    test=True,
    api_key="...",  # omit the api_key & secret to connect w/o authentication
    api_secret="...",
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
ws.orderbook_25_stream(handle_orderbook, "BTCPERP")


while True:
    # This while loop is required for the program to run. You may execute
    # additional code for your trading logic here.
    sleep(1)
