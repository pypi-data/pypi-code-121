from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from .database import DocumentDispatcher
from . import LBot
from graia.broadcast.entities.dispatcher import BaseDispatcher


class ContextDispatcher(BaseDispatcher):
    async def catch(self, interface: DispatcherInterface):
        if interface.annotation == LBot:
            return interface.annotation.get_running()
