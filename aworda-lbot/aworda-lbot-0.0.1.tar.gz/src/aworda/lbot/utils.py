from graia.broadcast import Broadcast
from graia.broadcast.entities.dispatcher import BaseDispatcher
from src.aworda.lbot.dispatcher import ContextDispatcher, DocumentDispatcher


def global_dispatcher(broadcast: Broadcast):
    """
    全局广播器
    """
    broadcast.finale_dispatchers.append(ContextDispatcher())
    broadcast.finale_dispatchers.append(DocumentDispatcher())
