import datetime
from typing import TYPE_CHECKING, Optional

from .flags import UserFlags
from .settings import UserSettings

if TYPE_CHECKING:
    from .client import Client

class User:
    def __init__(
        self,
        client: "Client",
        **data
    ):
        self.id: int = int(data['id'])
        self.username: str = data['username']
        self.discriminator: int = data['discriminator']
        if data.get('email'):
            self.email: str = data['email']
        self.flags = UserFlags(data['flags'])
        self.locale: str = data['locale']
        self.joined_at: datetime.datetime = datetime.datetime.fromisoformat(data['joined_at'])
        self.bio: str = data['bio']
        self.verified: bool = data['verified']
        self.system: bool = data['system']
        self.bot: bool = data['bot']
        self.pronouns: str = data['pronouns']
        self._client = client

    async def create_note(self, content: str):
        if hasattr(self, 'edit'):
            raise Exception('Cannot add a note to yourself')

        await self._client._http.create_user_note(
            self.id, content=content
        )

class ClientUser(User):
    async def edit(
        self,
        username: Optional[str] = None,
        discriminator: Optional[int] = None,
        pronouns: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None
    ):
        await self._client._http.edit_me(
            username=username,
            discriminator=discriminator,
            pronouns=pronouns,
            email=email,
            password=password
        )

        if username:
            self.username = username
        if discriminator:
            self.discriminator = discriminator
        if pronouns:
            self.pronouns = pronouns
        if email:
            self.email = email

    async def verify(self, code: int):
        if self.verified:
            raise Exception('Already Verified')

        await self._client._http.verify_email(code)

    @property
    async def settings(self):
        r = await self._client._http.get_settings()

        return UserSettings(
            self._client,
            r['theme'],
            r['guild_placements'],
            r['direct_message_ignored_guilds']
        )
