import asyncio
from swidgetdevice import SwidgetDevice

dev = SwidgetDevice("192.168.1.143")
asyncio.run(dev.update())