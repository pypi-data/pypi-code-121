from typing import TYPE_CHECKING, List, Optional

from .flags import GuildPermissions
from .role import Role

if TYPE_CHECKING:
    from .client import Client

class Guild:
    def __init__(self, client: "Client", **data):
        self._client = client
        self.id = int(data['id'])
        self.name: str = data['name']
        self.description: str = data['description']
        self.vanity_url: str = data['vanity_url']
        self.owner_id = int(data['owner_id'])
        self.nsfw: bool = data['nsfw']
        self.large: bool = data['large']
        self.perferred_locale: str = data['perferred_locale']
        self.permissions = GuildPermissions(int(data['permissions']))
        self.features: List[str] = data['features']
        self.verified: bool = data['verified']

    async def edit(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        nsfw: Optional[bool] = None
    ):
        r = await self._client._http.edit_guild(
            guild_id=self.id, name=name, description=description, nsfw=nsfw
        )


    async def get_roles(self) -> List[Role]:
        roles = []
        rs = await self._client._http.get_roles(self.id)
        for role in rs:
            roles.append(Role(role))
        return roles
