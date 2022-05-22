from types import TracebackType
from typing import Union
from graia.ariadne.message.chain import MessageChain
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from graia.ariadne.event.message import MessageEvent
from graia.broadcast.exceptions import ExecutionStop
from graia.ariadne import get_running
from . import LBot
from typing import Optional


class PersonPermission(BaseDispatcher):
    def __init__(self, sender: int, denied_message: Union[MessageChain, str] = None):
        self.sender = sender
        if isinstance(denied_message, str):
            self.denied_message = MessageChain.create(denied_message)
        else:
            self.denied_message = denied_message

    async def afterDispatch(
        self,
        interface: DispatcherInterface,
        exception: Optional[Exception],
        tb: Optional[TracebackType],
    ):
        if interface.event.sender.id != self.sender:
            if self.denied_message:
                app = get_running()
                await app.sendMessage(interface.event, self.denied_message)
            raise ExecutionStop()

    async def catch(self, interface: DispatcherInterface):
        return await super().catch(interface)


class MasterPermission(PersonPermission):
    def __init__(self, denied_message: Union[MessageChain, str] = None):
        lbot = LBot.get_running()
        sender = lbot.config.bot.master
        super().__init__(sender, denied_message)
