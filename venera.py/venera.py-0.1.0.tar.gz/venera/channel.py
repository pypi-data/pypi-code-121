from typing import TYPE_CHECKING, List, Optional

from .flags import from_list, PermissionOverwrite
from .guild import Guild

if TYPE_CHECKING:
    from .client import Client

class BaseChannel:
    def __init__(self, client: "Client", **data):
        self._client = client
        self.id = int(data['id'])
        self.type: int = data['type']
        self.position: int = data['position']
        self.name: str = data['name']
        self.topic: str = data['topic']
        self.slowmode_timeout: int = data['slowmode_timeout']
        self.parent_id: int = data['parent_id']
        self.permission_overwrites = from_list(data['permission_overwrites'])
        self.guild = Guild(client, **data['guild'])

    async def edit(
        self,
        name: Optional[str] = None,
        topic: Optional[str] = None,
        position: Optional[int] = None,
        permission_overwrites: Optional[List[PermissionOverwrite]] = None,
        slowmode_timeout: Optional[int] = None,
        parent_id: Optional[int] = None
    ):
        permo = None

        if permission_overwrites:
            permo = []
            for overwrite in permission_overwrites:
                permo.append({'allow': overwrite.allow, 'deny': overwrite.deny, 'user_id': overwrite.user_id})

        await self._client._http.edit_channel(
            self.guild.id,
            self.id,
            name=name,
            topic=topic,
            position=position,
            permission_overwrites=permo,
            slowmode_timeout=slowmode_timeout,
            parent_id=parent_id
        )

        if name:
            self.name = name
        if topic:
            self.topic = topic
        if position:
            self.position = position
        if permission_overwrites:
            self.permission_overwrites = permission_overwrites
        if slowmode_timeout:
            self.slowmode_timeout = slowmode_timeout
        if parent_id:
            self.parent_id = parent_id

    async def delete(self):
        await self._client._http.delete_channel(self.guild.id, self.id)

class Category(BaseChannel):
    ...

class TextChannel(BaseChannel):
    async def send(self, content: str, *, replied_message: Optional[int] = None):
        await self._client._http.create_message(
            self.guild.id, self.id, content, replied_message
        )

    #async def get_message(self, message_id: int):
        #return Message(self._client, **await self._client._http.get_message(self.guild.id, self.id, message_id=message_id))

    #async def get_messages(self):
        #msgs = []

        #resp = await self._client._http.get_messages(self.guild.id, self.id)

        #for message in resp:
            #message['channel'] = self
            #msgs.append(Message(self._client, **message))

        #return msgs
