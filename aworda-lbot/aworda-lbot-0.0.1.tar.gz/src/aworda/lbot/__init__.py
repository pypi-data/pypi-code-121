from graia.ariadne.app import Ariadne
from graia.broadcast import Broadcast
from motor.motor_asyncio import AsyncIOMotorClient
from .config import AwordaConfig
from contextvars import ContextVar

context = ContextVar("aworda_lbot_context")


class LBot:
    def __init__(
        self, broadcast: Broadcast = Broadcast(), config_path: str = "config.json"
    ):
        self.config = AwordaConfig.from_json_file(config_path)
        self.app = Ariadne(self.config.mirai, broadcast=broadcast)
        self.context = context.set(self)
        self.loop = broadcast.loop
        self.broadcast = broadcast
        self.motor_client = AsyncIOMotorClient(self.config.db.url, io_loop=self.loop)

    def launch_blocking(self):
        self.app.launch_blocking()

    @classmethod
    def get_running(cls) -> "LBot":
        return context.get()
