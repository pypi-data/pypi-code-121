from typing import List, Literal, Union

import aiohttp

class HTTPException(Exception):
    pass

class HTTPClient:
    def __init__(self, token: str):
        self._token = token
        self._headers = {
            'Authorization': token,
            'User-Agent': 'venera.py'
        }
        self._session = None
        self._base_url = 'https://concord.chat/api/v5'

    async def check_session(self):
        if not self._session:
            self._session = aiohttp.ClientSession(headers=self._headers)

    async def request(self, method: str, prefix: str, data: dict = None):
        await self.check_session()

        r = await self._session.request(method, self._base_url + prefix, json=data)

        if not r.ok and r.status != 404:
            raise HTTPException(r.status, await r.text())

        return r

    # START SECTION USERS #

    @classmethod
    async def login(cls, email: str, password: str):
        cs = aiohttp.ClientSession()

        r = await cs.get(
            'https://concord.chat/api/v5/users/@me/tokens',
            json={
                'email': email,
                'password': password
            }
        )

        if r.status != 201:
            raise HTTPException('Failed to Login to Account')

        token = await r.json()[0]
        await cs.close()

        return cls(token)

    @classmethod
    async def signup(
        cls,
        email: str,
        password: str,
        username: str,
        locale: str = None,
        bio: str = None,
        pronouns: str = None
    ):
        cs = aiohttp.ClientSession()
        data = {
            'email': email,
            'password': password,
            'username': username
        }

        if locale:
            data['locale'] = locale

        if bio:
            data['bio'] = bio

        if pronouns:
            data['pronouns'] = pronouns

        r = await cs.post(
            'https://concord.chat/api/v5/users',
            json=data
        )

        if r.status != 201:
            raise HTTPException(r.status, await r.text())

        resp = cls(await r.json()['token'])
        return resp, await r.json()

    async def get_me(self):
        r = await self.request('GET', '/users/@me')
        return await r.json()

    async def get_user(self, user_id: int):
        r = await self.request('GET', f'/users/{user_id}')
        return await r.json()

    async def edit_me(
        self,
        username: str = None,
        discriminator: int = None,
        pronouns: str = None,
        email: str = None,
        password: str = None
    ):
        d = {}

        if username:
            d['username'] = username

        if discriminator:
            d['discriminator'] = discriminator

        if pronouns:
            d['pronouns'] = pronouns

        if email:
            d['email'] = email

        if password:
            d['password'] = email

        r = await self.request('PATCH', '/users/@me', d)
        return await r.json()

    async def verify_email(self, code: int):
        try:
            r = await self.request(
                'POST',
                f'/users/@me/verify?utm_verification={code}'
            )
            return await r.json()
        except:
            raise HTTPException('Invalid Verification Code Given')

    async def get_settings(self):
        r = await self.request('GET', '/user/@me/meta')
        return await r.json()

    async def edit_settings(
        self,
        theme: Union[Literal['dark'], Literal['light']] = None,
        guild_placements: List[int] = None,
        direct_message_ignored_guilds: List[int] = None
    ):
        d = {}

        if theme:
            d['theme'] = theme

        if guild_placements:
            d['guild_placements'] = guild_placements

        if direct_message_ignored_guilds:
            d['direct_message_ignored_guilds'] = direct_message_ignored_guilds

        r = await self.request('PATCH', '/users/@me/meta', d)

    async def get_user_note(self, user_id: int):
        r = await self.request('GET', f'/users/@me/notes/{user_id}')
        if r.status == 404:
            return {'s': 'notfound'}

        return await r.json()

    async def create_user_note(
        self,
        user_id: int,
        content: str
    ):
        r = await self.request(
            'PUT',
            f'/users/@me/notes/{user_id}',
            {'content': content}
        )

        return await r.json()

    # END SECTION USERS #
    # START SECTION GUILDS #

    async def get_joined_guilds(self):
        r = await self.request(
            'GET', '/users/@me/guilds'
        )
        return await r.json()

    async def get_guild_user_settings(self, guild_id: int):
        r = await self.request('GET', f'/users/@me/guilds/{guild_id}/meta')
        return await r.json()

    async def edit_guild_user_settings(self, guild_id: int, muted_channels: List[int] = None):
        d = {}

        if muted_channels:
            d['muted_channels'] = muted_channels

        r = await self.request('PATCH', f'/users/@me/guilds/{guild_id}/meta', d)

        return await r.json()

    async def create_guild(
        self,
        name: str,
        description: str = None,
        nsfw: bool = False
    ):
        d = {
            'name': name,
            'description': description
        }

        if nsfw:
            d['nsfw'] = True

        r = await self.request('POST', '/guilds', d)

        return await r.json()

    async def edit_guild(
        self,
        guild_id: int,
        name: str = None,
        description: str = None,
        nsfw: bool = None
    ):
        d = {}

        if name:
            d['name'] = name

        if description:
            d['description'] = description

        if nsfw is not None:
            d['nsfw'] = nsfw

        r = await self.request('PATCH', f'/guilds/{guild_id}', d)

        return await r.json()

    async def delete_guild(
        self, guild_id: int
    ):
        r = await self.request('DELETE', f'/guilds/{guild_id}')

        return await r.json()

    async def get_guild(self, guild_id: int):
        r = await self.request('GET', f'/guilds/{guild_id}')

        if r.status == 404:
            return {'s': 'notfound'}

        return await r.json()

    async def create_invite(self, guild_id: int, channel_id: int, ttl: int = None):
        if ttl:
            d = {'ttl': ttl}
        else:
            d = None

        r = await self.request(
            'POST',
            f'/guilds/{guild_id}/channels/{channel_id}/invites',
            d    
        )

        return await r.json()

    async def claim_vanity(self, guild_id: int, code: str):
        r = await self.request('PUT', f'/guilds/{guild_id}/vanity?utm_vanity={code}')
        return await r.json()

    # END SECTION GUILDS #
    # START SECTION MEMBERS #

    async def get_member(self, guild_id: int, user_id: int):
        r = await self.request('GET', f'/guilds/{guild_id}/members/{user_id}')

        if r.status == 404:
            return {'s': 'notfound'}

        return await r.json()

    async def get_members(self, guild_id: int):
        r = await self.request('GET', f'/guilds/{guild_id}/members')

        return await r.json()

    async def edit_my_member(self, guild_id: int, nick: str = None):
        d = {}

        if nick:
            d['nick'] = nick

        r = await self.request('PATCH', f'/guilds/{guild_id}/members/@me')

        return await r.json()

    async def edit_member(
        self,
        guild_id: int,
        member_id: int,
        nick: str = None,
        roles: List[int] = None
    ):
        d = {}

        if nick:
            d['nick'] = nick

        if roles:
            d['roles'] = roles

        r = await self.request(
            'PATCH',
            f'/guilds/{guild_id}/members/{member_id}/nick',
            d
        )

        return await r.json()

    # END SECTION MEMBERS #
    # START SECTION AUDITS #

    async def get_guild_logs(self, guild_id: int):
        r = await self.request('GET', f'/guilds/{guild_id}/audits')
        return await r.json()

    async def get_guild_log(self, guild_id: int, log_id: int):
        r = await self.request('GET', f'guilds/{guild_id}/audits/{log_id}')
        return await r.json()

    async def create_log(
        self,
        guild_id: int,
        type: str,
        postmortem: str,
        audited: int = None,
        object_id: int = None
    ):
        d = {
            'type': type,
            'postmortem': postmortem
        }

        if audited:
            d['audited'] = audited

        if object_id:
            d['object_id'] = object_id
    
        r = await self.request('POST', f'/guilds/{guild_id}/audits', d)

        return await r.json()

    # END SECTION AUDITS #
    # START SECTION ROLES #

    async def create_role(self):
        raise NotImplementedError

    async def edit_role(self):
        raise NotImplementedError

    async def get_role(self, guild_id: int, role_id: int):
        r = await self.request('GET', f'/guilds/{guild_id}/roles/{role_id}')
        return await r.json()

    async def get_roles(self, guild_id: int):
        r = await self.request('GET', f'/guilds/{guild_id}/roles')
        return await r.json()

    # END SECTION ROLES #
    # START SECTION CHANNELS #

    async def create_channel(
        self,
        guild_id: int,
        type: int,
        position: int,
        parent_id: int = None,
        slowmode_timeout: int = None,
    ):
        d = {
            'type': type,
            'position': position,
        }
    
        if parent_id:
            d['parent_id'] = parent_id

        if slowmode_timeout:
            d['slowmode_timeout'] = slowmode_timeout
    
        r = await self.request(
            'POST', f'/guilds/{guild_id}/channels'
        )

        return await r.json()

    async def edit_channel(
        self,
        guild_id: int,
        channel_id: int,
        name: str = None,
        topic: str = None,
        position: int = None,
        permission_overwrites: List[dict] = None,
        slowmode_timeout: int = None,
        parent_id: int = None
    ):
        d = {}

        if name:
            d['name'] = name

        if topic:
            d['topic'] = topic

        if position:
            d['position'] = position
    
        if permission_overwrites:
            d['permission_overwrites'] = permission_overwrites

        if slowmode_timeout:
            d['slowmode_timeout'] = slowmode_timeout

        if parent_id:
            d['parent_id'] = parent_id

        r = await self.request(
            'PATCH', f'/guilds/{guild_id}/channels/{channel_id}', d
        )

        return await r.json()

    async def delete_channel(self, guild_id: int, channel_id: int):
        r = await self.request('DELETE', f'/guilds/{guild_id}/channels/{channel_id}')
        return await r.json()

    async def get_channel(self, guild_id: int, channel_id: int):
        r = await self.request('GET', f'/guilds/{guild_id}/channels/{channel_id}')
        return await r.json()

    async def get_channels(self, guild_id: int):
        r = await self.request('GET', f'/guilds/{guild_id}/channels')
        return await r.json()

    # END SECTION CHANNELS #
    # START SECTION READSTATES #

    async def ack_message(self, guild_id: int, channel_id: int, message_id: int):
        r = await self.request(
            'POST',
            f'/guilds/{guild_id}/channels/{channel_id}/messages/{message_id}/ack'
        )
        return await r.json()

    async def get_readstate(self, guild_id: int, channel_id: int):
        r = await self.request(
            'GET', f'/guilds/{guild_id}/channels/{channel_id}/readstate'
        )
        return await r.json()

    async def get_readstates(self):
        r = await self.request('GET', '/readstates')
        return await r.json()

    # END SECTION READSTATES #
    # START SECTION MESSAGES #

    async def get_message(self, guild_id: int, channel_id: int, message_id: int):
        r = await self.request(
            'GET',
            f'/guilds/{guild_id}/channels/{channel_id}/messages/{message_id}'
        )
        return await r.json()

    async def get_messages(self, guild_id: int, channel_id: int):
        r = await self.request(
            'GET',
            f'/guilds/{guild_id}/channels/{channel_id}/messages'
        )
        return await r.json()

    async def create_message(
        self,
        guild_id: int,
        channel_id: int,
        content: str,
        referenced_message_id: int = None
    ):
        d = {
            'content': content
        }

        if referenced_message_id:
            d['referenced_message_id'] = referenced_message_id

        r = await self.request(
            'POST', f'/guilds/{guild_id}/channels/{channel_id}/messages', d
        )

        return await r.json()

    async def edit_message(
        self,
        guild_id: int,
        channel_id: int,
        message_id: int,
        content: str = None
    ):
        d = {}

        if content:
            d['content'] = content

        r = await self.request(
            'PATCH', f'/guilds/{guild_id}/channels/{channel_id}/messages/{message_id}'
        )
        return await r.json()

    async def delete_message(self, guild_id: int, channel_id: int, message_id: int):
        r = await self.request('DELETE', f'/guilds/{guild_id}/channels/{channel_id}/messages/{message_id}')
        return await r.json()

    async def pin(self, guild_id: int, channel_id: int, message_id: int):
        r = await self.request('POST', f'/guilds/{guild_id}/channels/{channel_id}/pins/{message_id}')
        return await r.json()

    async def unpin(self, guild_id: int, channel_id: int, message_id: int):
        r = await self.request('DELETE', f'/guilds/{guild_id}/channel/{channel_id}/pins/{message_id}')
        return await r.json()

    # END SECTION MESSAGES #
