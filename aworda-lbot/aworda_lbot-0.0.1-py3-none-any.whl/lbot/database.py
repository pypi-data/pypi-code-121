from beanie import Document
import beanie
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from . import LBot


class DocumentDispatcher(BaseDispatcher):
    async def catch(self, interface: DispatcherInterface) -> object:
        if issubclass(interface.annotation, Document):
            lbot = LBot.get_running()
            db = lbot.motor_client[interface.name]
            await beanie.init_beanie(
                database=db, document_models=[interface.annotation]
            )
            return interface.annotation.__class__
