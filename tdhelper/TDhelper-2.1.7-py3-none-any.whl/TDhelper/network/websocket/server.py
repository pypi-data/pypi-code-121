#! python 3.6

#########################################################
#| @File    :   server.py
#| @ClsName :   server.p
#| @Version :   1.0.0
#| @History :
#|-----------------------------------------------------------------|
#| Type   | Author   | Contact           | Time                    |
#|-----------------------------------------------------------------|
#| Create | Tony.don | yeihizhi@163.com  | 2021-10-30 23:18:48     |
#|-----------------------------------------------------------------|
#| @License :   MIT
#| @Desc    :   create an websocket server.
#########################################################

# import lib by pypi
import asyncio
import json
from websockets import serve
# import lib by project
from protocol import webProtocol


class p(webProtocol):
    async def protocolAnalysis(self,websocket,msg):
        await websocket.send(msg)

    async def response(self,websocket):
        pass
        

class tdWebSocket:
    def __init__(self,protocolModule):
        self.module= protocolModule()
        loop= asyncio.get_event_loop()
        loop.run_until_complete(self.main())

    async def conected(self,websocket,path):
        async for msg in websocket:
            await self.module.protocolAnalysis(websocket,msg)

    async def main(self):
        async with serve(self.conected, "127.0.0.1", 8765):
            await asyncio.Future()

if __name__ == "__main__":
    ccc= tdWebSocket(p)