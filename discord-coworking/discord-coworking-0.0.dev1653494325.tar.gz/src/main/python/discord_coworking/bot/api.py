from discord import Message, Client


class MessageHandler:

    async def __call__(self, client: Client, message: Message):
        if not self.accept(message):
            return
        await self.handle(client, message)

    def accept(self, message: Message) -> bool:
        raise NotImplementedError()

    async def handle(self, client: Client, message: Message):
        raise NotImplementedError()