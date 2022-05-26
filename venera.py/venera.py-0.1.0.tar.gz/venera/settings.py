from typing import TYPE_CHECKING, List, Literal, Union

if TYPE_CHECKING:
    from .client import Client

class UserSettings:
    def __init__(
        self,
        client: "Client",
        theme: str,
        guild_placements: List[int],
        direct_message_ignored_guilds: List[int]
    ):
        self.theme = theme
        self.guild_placements = guild_placements
        self.direct_message_ignored_guilds = direct_message_ignored_guilds
        self._client = client

    async def edit(
        self,
        theme: Union[
            Literal['dark'],
            Literal['light']
        ] = None,
        guild_placements: List[int] = None,
        direct_message_ignored_guilds: List[int] = None
    ):
        await self._client._http.edit_settings(
            theme=theme,
            guild_placements=guild_placements,
            direct_message_ignored_guilds=direct_message_ignored_guilds
        )

        if theme:
            self.theme = theme
        if guild_placements:
            self.guild_placements = guild_placements
        if direct_message_ignored_guilds:
            self.direct_message_ignored_guilds = direct_message_ignored_guilds

class GuildSettings:
    def __init__(self, client: "Client", guild_id: int, muted_channels: List[int] = None):
        self._client = client
        self.guild_id = guild_id
        self.muted_channels = muted_channels
    
    async def edit(self, muted_channels: List[int] = None):
        await self._client._http.edit_guild_user_settings(
            guild_id=self.guild_id,
            muted_channels=muted_channels
        )

        if muted_channels:
            self.muted_channels = muted_channels
