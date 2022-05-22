#! python 3.6

#########################################################
# | @File    :   protocol.py
# | @ClsName :   TDhelper.network.websocket.protocol.webProtocol
# | @Version :   1.0.0
# | @History :
# |-----------------------------------------------------------------|
# | Type   | Author   | Contact           | Time                    |
# |-----------------------------------------------------------------|
# | Create | Tony.don | yeihizhi@163.com  | 2021-10-30 23:23:02     |
# |-----------------------------------------------------------------|
# | @License :   MIT
# | @Desc    :   webosocket action protocol.
#########################################################

# import lib by pypi
import abc
import asyncio
import json

# import lib by project


class webProtocol(metaclass=abc.ABCMeta):
    def __init__(self, authorize=False):
        """__init__

        webProtocol abstract class.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        """
        self.isAuthorize = authorize
        self.usr_list = {}

    async def authorize(self, websocket, token):
        """authorize

        user connect authorize. if authorize success then insert this client handle in usr_list.

        Args:
            websocket (websocket): client websocket handle.

        Returns:
            True: authorize success.
            Flase: authorize fail.

        Raises:
            None.

        """
        self.usr_list = {token: websocket}
        # todo:  authorize.
        return False

    async def loginout(self, websocket, token):
        '''loginout
        
        user login out server.
        
        Args:
            websocket (websocket): client handle.
            token (string): user token.
        
        Returns:
            None.
        
        Raises:
            None.
        
        '''
        if self.usr_list[token]:
            self.usr_list[token] = None

    async def disableconnection(self, websocket, token=None):
        '''disableconnection
        
        disable an connection websocket.
        
        Args:
            websocket (websocket): client handle.
            token (object): user token.
        
        Returns:
            None.
        
        Raises:
            None.
        
        '''
        if not token:
            await self.loginout(websocket, token)
        try:
            await websocket.wait_close()
        except Exception as e:
            pass

    async def ping(self, websocket, data=None):
        try:
            pong_waiter = await websocket.ping(data)
            await pong_waiter
        except Exception as e:
            await self.disableconnection(websocket)

    @abc.abstractclassmethod
    async def protocolAnalysis(self, websocket, msg):
        '''protocolAnalysis
        
        Analysis action protocol command, router action method.
        
        Args:
            websocket (websocket): client handle.
            msg (object): server recv client msg. 
        
        Returns:
            None.
        
        Raises:
            None.
        
        '''
        pass

    @abc.abstractclassmethod
    async def response(self, websocket):
        '''response
        
        response msg to client.
        
        Args:
            websocket (websocket): client handle.
        
        Returns:
            None.
        
        Raises:
            None.
        
        '''
        pass
