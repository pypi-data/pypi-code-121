from pybit import inverse_perpetual
from pybit import spot
from time import sleep

# Set up logging (optional)
import logging
logging.basicConfig(filename="pybit.log", level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")
def kline_stream_callback(message):
    print(message)
ws_spot = spot.WebSocket(test=False)
ws_spot.kline_v1_stream(kline_stream_callback, "BTCUSDT", "1m")
while True:
    sleep(1)