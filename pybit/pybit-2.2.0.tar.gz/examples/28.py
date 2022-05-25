from pybit import usdt_perpetual
client = usdt_perpetual.WebSocket(test=False, trace_logging=False)
from time import sleep
sleep(5)
client.exit()
