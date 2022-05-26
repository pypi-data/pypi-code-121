from typing import TYPE_CHECKING, List
from datetime import datetime

from .user import User
from .guild import Guild
from .channel import TextChannel

if TYPE_CHECKING:
    from .client import Client

class Message:
    def __init__(self, client: "Client", **data):
        self._client = client
        self.id: int = data['id']
        self.guild = Guild(client, **data['guild'])
        self.author = User(client, **data['author'])
        self.channel = TextChannel(client, **data['channel'])
        self.content: str = data['content']
        self.created_at: datetime = datetime.fromisoformat(data['created_at'])
        self.last_edited: datetime = datetime.fromisoformat(data['last_edited'])
        self.tts: bool = data['tts']
        self.mentions_everyone: bool = data['mentions_everyone']
        self.mentioned_users: List[int] = data['mentioned_users']
        self.pinned: bool = data['pinned']
        self.replied_to: int = data['referenced_message_id']

    async def send(self, content: str, **kwargs):
        return await self.channel.send(content, **kwargs)

    async def reply(self, content: str, **kwargs):
        return await self.channel.send(content, replied_message=self.id, **kwargs)
