from typing import TYPE_CHECKING

from .flags import GuildPermissions

if TYPE_CHECKING:
    from .client import Client

class Role:
    def __init__(self, client: "Client", **data):
        self.id: int = int(data['id'])
        self.name: str = data['name']
        self.color: int = data['color']
        self.hoist: bool = data['hoist']
        self.position: int = data['position']
        self.permissions = GuildPermissions(int(data['permissions']))
        self.mentionable: bool = data['mentionable']
        self._client = client

    async def edit(self):
        await self._client._http.edit_role()
