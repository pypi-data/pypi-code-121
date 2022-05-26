from .errors import *
from typing import Optional, Any, List, TypeVar, Dict
from aiohttp import ClientResponse

ISO8601_timestamp = TypeVar('ISO8601_timestamp')

class Paths:

    def __init__(self, client):
        self._client = client

    """
    Audit Log
    """

    async def get_audit_logs(self, guild_id: int, limit = 50, before = None, user_id = None, action_type = None) -> ClientResponse:
        """Get the audit logs for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild.
        limit : int
            The number of entries to return.
        before : int
            Entries that preceded a specific audit log entry ID
        user_id : int
            The ID of the user to filter the logs by.
        action_type : int
            The type of action to filter the logs by.

        Returns
        -------
        ClientResponse
            A list of audit logs.

        Raises
        ------
        InvalidParams
            The limit is not between 1 and 100.
        """
        if 1 > limit or limit > 100:
            raise InvalidParams('limit must be between 1 and 100')

        path = f'/guilds/{guild_id}/audit-logs'
        bucket = 'GET' + path

        params = {'limit': limit}
        if before is not None:
            params['before'] = before
        if user_id is not None:
            params['user_id'] = user_id
        if action_type is not None:
            params['action_type'] = action_type

        return await self._client._request('GET', path, bucket, params=params)

    """
    Channel
    """

    async def get_channel(self, channel_id: int) -> ClientResponse:
        """Get a channel by ID.

        Parameters
        ----------
        channel_id : int
            The ID of the channel you wish to get information about.

        Returns
        -------
        ClientResponse
            Channel information.
        """
        path = f'/channels/{channel_id}'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def edit_channel(self, channel_id: int, *, reason: Optional[str] = None, **options: Any) -> ClientResponse:
        """Update a channel's settings.

        Parameters
        ----------
        channel_id : int
            The ID of the channel you wish to edit.
        reason : Optional[str], optional
            A reason for this edit that will be displayed in the audit log, by default None
        options : Any
            The params required to update the required aspects of the channel.

        Returns
        -------
        ClientResponse
            A dict containing a channel object.
        """
        path = f'/channels/{channel_id}'
        bucket = 'PATCH' + path
        valid_keys = (
            'name',
            'parent_id',
            'topic',
            'bitrate',
            'nsfw',
            'user_limit',
            'position',
            'permission_overwrites',
            'rate_limit_per_user',
            'type',
            'rtc_region',
            'video_quality_mode',
            'archived',
            'auto_archive_duration',
            'locked',
            'invitable',
            'default_auto_archive_duration',
            'flags',
        )
        payload = {k: v for k, v in options.items() if k in valid_keys}
        return await self._client._request('PATCH', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def delete_channel(self, channel_id: int, reason: str = None) -> ClientResponse:
        """Delete a channel, or close a private message.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to be deleted/closed.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The responce from Discord.
        """
        path = f'/channels/{channel_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    async def get_channel_messages(self, channel_id: int, limit=50, before: int = None, after: int = None, around: int = None) -> ClientResponse:
        """Get messages from a channel.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to get message from
        limit : int, optional
            Max number of messages to return (1-100), by default 50
        before : int, optional
            Get messages before this message ID, by default None
        after : int, optional
            Get messages after this message ID, by default None
        around : int, optional
            Get messages around this message ID, by default None

        Returns
        -------
        ClientResponse
            A list of message objects.

        Raises
        ------
        InvalidParams
            The limit is not between 1 and 100.
        """
        if 1 > limit or limit > 100:
            raise InvalidParams('limit must be between 1 and 100')
        path = f'/channels/{channel_id}/messages'
        bucket = 'GET' + path

        params = {
            'limit': limit,
        }

        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        if around is not None:
            params['around'] = around

        return await self._client._request('GET', path, bucket, params=params)

    async def get_message(self, channel_id: int, message_id: int) -> ClientResponse:
        """Get a message from a channel.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to get message from.
        message_id : int
            The ID of the message that is to be retrieved.

        Returns
        -------
        ClientResponse
            A message object.
        """
        path = f'/channels/{channel_id}/messages/{message_id}'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def create_message(self, channel_id: int, content: str = None, tts: bool = None, embeds: List[dict] = None, allowed_mentions: Any = None, message_reference: Any = None, components: List[Any] = None, sticker_ids: List[int] = None) -> ClientResponse:
        """Post a message to a guild text or DM channel.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to send a message to.
        content : str, optional
            Message contents (up to 2000 characters), by default None
        tts : bool, optional
            true if this is a TTS message, by default None
        embeds : List[dict], optional
            An array of dicts containing embed data, by default None
        allowed_mentions : Any, optional
            Allowed mentions for the message, by default None
        message_reference : Any, optional
            Include to make your message a reply, by default None
        components : List[Any], optional
            An array of components to include with the message, by default None
        sticker_ids : List[int], optional
            IDs of up to 3 stickers in the server to send in the message, by default None

        Returns
        -------
        ClientResponse
            A message object

        Raises
        ------
        InvalidParams
            content, embeds or sticker_ids must be provided.
        """
        if content is None and embeds is None and sticker_ids is None:
            raise InvalidParams('content, embeds or sticker_ids must be provided')
        path = f'/channels/{channel_id}/messages'
        bucket = 'POST' + path

        payload = {}

        if content is not None:
            payload['content'] = content
        if tts is not None:
            payload['tts'] = tts
        if embeds is not None:
            payload['embeds'] = embeds
        if allowed_mentions is not None:
            payload['allowed_mentions'] = allowed_mentions
        if message_reference is not None:
            payload['message_reference'] = message_reference
        if components is not None:
            payload['components'] = components
        if sticker_ids is not None:
            payload['sticker_ids'] = sticker_ids

        return await self._client._request('POST', path, bucket, json=payload)

    async def crosspost_message(self, channel_id: int, message_id: int) -> ClientResponse:
        """Crosspost a message in a News Channel to following channels.

        Parameters
        ----------
        channel_id : int
            The ID of the channel the message to be corssposted is in.
        message_id : int
            The ID of the message to be crossposted.

        Returns
        -------
        ClientResponse
            A message object.
        """
        path = f'/channels/{channel_id}/messages/{message_id}/crosspost'
        bucket = 'POST' + path
        return await self._client._request('POST', path, bucket)

    async def add_reaction(self, channel_id: int, message_id: int, emoji: str) -> ClientResponse:
        """Create a reaction for a message.

        Parameters
        ----------
        channel_id : int
            The ID of the channel the message is in.
        message_id : int
            The ID of the message to add a reaction to.
        emoji : str
            The emoji to react with.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me'
        bucket = 'PUT' + path
        return await self._client._request('PUT', path, bucket)

    async def remove_own_reaction(self, channel_id: int, message_id: int, emoji: str) -> ClientResponse:
        """Remove a reaction from a message.

        Parameters
        ----------
        channel_id : int
            The ID of the channel the message is in.
        message_id : int
            The ID of the message to remove a reaction from.
        emoji : str
            The emoji to remove.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket)

    async def remove_reaction(self, channel_id: int, message_id: int, emoji: str, member_id: int) -> ClientResponse:
        """Remove a users reaction from a message.

        Parameters
        ----------
        channel_id : int
            The ID of the channel the message is in.
        message_id : int
            The ID of the message to remove a reaction from.
        emoji : str
            The emoji to remove.
        member_id : int
            The ID of the member thats reaction will be removed.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{member_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket)

    async def get_reactions(self, channel_id: int, message_id: int, emoji: str, limit: int = 25, after: int = None) -> ClientResponse:
        """Get a list of users that reacted with this emoji.

        Parameters
        ----------
        channel_id : int
            The ID of the channel the message is in.
        message_id : int
            The ID of the message to get reactions from.
        emoji : str
            The emoji to get reactions for.
        limit : int, optional
            Max number of users to return (1-100), by default 25
        after : int, optional
            Get users after this user ID, by default None

        Returns
        -------
        ClientResponse
            A list of user objects.
        """
        path = f'/channels/{channel_id}/messages/{message_id}/reactions/{emoji}'
        bucket = 'GET' + path
        params = {
            'limit': limit,
        }
        if after is not None:
            params['after'] = after

        return await self._client._request('GET', path, bucket, params=params)

    async def clear_reactions(self, channel_id: int, message_id: int) -> ClientResponse:
        """Deletes all reactions on a message.

        Parameters
        ----------
        channel_id : int
            The ID of the channel the message is in.
        message_id : int
            The ID of the message to clear reactions from.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/messages/{message_id}/reactions'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket)

    async def clear_single_reaction(self, channel_id: int, message_id: int, emoji: str) -> ClientResponse:
        """Deletes all the reactions for a given emoji on a message.

        Parameters
        ----------
        channel_id : int
            The ID of the channel the message is in.
        message_id : int
            The ID of the message to clear reactions from.
        emoji : str
            The emoji to clear reactions for.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/messages/{message_id}/reactions/{emoji}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket)

    async def edit_message(self, channel_id: int, message_id: int, content: str = None, embeds: List[dict] = None, allowed_mentions: Any = None, components: List[Any] = None) -> ClientResponse:
        """Edit a previously sent message.

        Parameters
        ----------
        channel_id : int
            The ID of the channel the message is in.
        message_id : int
            The ID of the message to edit.
        content : str, optional
            Message contents (up to 2000 characters), by default None
        embeds : List[dict], optional
            An array of dicts containing embed data, by default None
        allowed_mentions : Any, optional
            Allowed mentions for the message, by default None
        components : List[Any], optional
            An array of components to include with the message, by default None

        Returns
        -------
        ClientResponse
            _description_
        """
        path = f'/channels/{channel_id}/messages/{message_id}'
        bucket = 'PATCH' + path
        payload = {}

        if content is not None:
            payload['content'] = content
        if embeds is not None:
            payload['embeds'] = embeds
        if allowed_mentions is not None:
            payload['allowed_mentions'] = allowed_mentions
        if components is not None:
            payload['components'] = components

        self._request('PATCH', path, bucket, json=payload)

    async def delete_message(self, channel_id: int, message_id: int, reason: str = None) -> ClientResponse:
        """Delete a message.

        Parameters
        ----------
        channel_id : int
            The ID of the channel the message is in.
        message_id : int
            The ID of the message to delete.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/messages/{message_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    async def bulk_delete_messages(self, channel_id: int, message_ids: List[int], reason: str = None) -> ClientResponse:
        """Delete multiple messages.

        Parameters
        ----------
        channel_id : int
            The ID of the channel the messages are in.
        message_ids : List[int]
            The IDs of the messages to delete.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/messages/bulk-delete'
        bucket = 'POST' + path
        payload = {
            'messages': message_ids,
        }
        return await self._client._request('POST', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def edit_channel_permissions(self, channel_id: int, overwrite_id: int, allow: str, deny: str, type: int, reason: str = None) -> ClientResponse:
        """Edit the channel permission overwrites for a user or role in a channel.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to edit permissions for.
        overwrite_id : int
            The ID of the user or role to edit permissions for.
        allow : str
            The bitwise value of all allowed permissions.
        deny : str
            The bitwise value of all disallowed permissions.
        type : int
            0 for a role or 1 for a member
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/permissions/{overwrite_id}'
        bucket = 'PUT' + path
        payload = {'allow': allow, 'deny': deny, 'type': type}
        return await self._client._request('PUT', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def get_channel_invites(self, channel_id: int) -> ClientResponse:
        """Get a list of invites for a channel.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to get invites for.

        Returns
        -------
        ClientResponse
            A list of invite objects
        """
        path = f'/channels/{channel_id}/invites'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def create_channel_invite(self, channel_id: int, *, reason: str = None, max_age: int = 0, max_uses: int = 0, temporary: bool = False, unique: bool = True, target_type: int = None, target_user_id: int = None, target_application_id: int = None) -> ClientResponse:
        """Create a new invite for a channel.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to create an invite for.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None
        max_age : int, optional
            Duration of invite in seconds before expiry, by default 0
        max_uses : int, optional
            Max number of uses or 0 for unlimited, by default 0
        temporary : bool, optional
            Whether this invite only grants temporary membership, by default False
        unique : bool, optional
            If true, don't try to reuse a similar invite, by default True
        target_type : int, optional
            The type of target for this voice channel invite, by default None
        target_user_id : int, optional
            The id of the user whose stream to display for this invite, by default None
        target_application_id : int, optional
            The id of the embedded application to open for this invite, by default None

        Returns
        -------
        ClientResponse
            An invite object.
        """
        path = f'/channels/{channel_id}/invites'
        bucket = 'POST' + path
        payload = {
            'max_age': max_age,
            'max_uses': max_uses,
            'temporary': temporary,
            'unique': unique,
        }

        if target_type:
            payload['target_type'] = target_type

        if target_user_id:
            payload['target_user_id'] = target_user_id

        if target_application_id:
            payload['target_application_id'] = str(target_application_id)

        return await self._client._request('POST', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def delete_channel_permissions(self, channel_id: int, overwrite_id: int, reason: str = None) -> ClientResponse:
        """Delete a channel permission overwrite for a user or role in a channel.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to delete permissions for.
        overwrite_id : int
            The ID of the user or role to delete permissions for.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/permissions/{overwrite_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    async def follow_news_channel(self, channel_id: int, webhook_channel_id: int, reason: str = None) -> ClientResponse:
        """Follow a News Channel to send messages to a target channel.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to follow.
        webhook_channel_id : int
            ID of target channel.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/followers'
        bucket = 'POST' + path
        payload = {
            'webhook_channel_id': webhook_channel_id,
        }
        return await self._client._request('POST', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def start_typing(self, channel_id: int) -> ClientResponse:
        """Post a typing indicator for the specified channel.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to start the typing indicator in.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/typing'
        bucket = 'POST' + path
        return await self._client._request('POST', path, bucket)

    async def get_pinned_messages(self, channel_id: int) -> ClientResponse:
        """Get a list of pinned messages in a channel.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to get pinned messages for.

        Returns
        -------
        ClientResponse
            A list of message objects.
        """
        path = f'/channels/{channel_id}/pins'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def pin_message(self, channel_id: int, message_id: int, reason: str = None) -> ClientResponse:
        """Pin a message in a channel.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to pin the message in.
        message_id : int
            The ID of the message to pin.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/pins/{message_id}'
        bucket = 'PUT' + path
        return await self._client._request('PUT', path, bucket, headers={'X-Audit-Log-Reason': reason})

    async def unpin_message(self, channel_id: int, message_id: int, reason: str = None) -> ClientResponse:
        """Unpin a message in a channel.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to unpin the message in.
        message_id : int
            The ID of the message to unpin.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/pins/{message_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    async def add_group_recipient(self, channel_id: int, user_id: int, access_token: str, nickname: str = None) -> ClientResponse:
        """Adds a recipient to a Group DM using their access token.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to add the recipient to.
        user_id : int
            The ID of the user to add as a recipient.
        access_token : str
            Access token of a user.
        nickname : str, optional
            Nickname of the user being added, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/recipients/{user_id}'
        bucket = 'PUT' + path
        payload = {
            'access_token': access_token,
            'nick': nickname
        }
        return await self._client._request('PUT', path, bucket, json=payload)

    async def remove_group_recipient(self, channel_id: int, user_id: int) -> ClientResponse:
        """Removes a recipient from a Group DM.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to remove the recipient from.
        user_id : int
            The ID of the user to remove as a recipient.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/recipients/{user_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket)

    async def start_thread_from_message(self, channel_id: int, message_id: int, *, name: str, auto_archive_duration: int, rate_limit_per_user: int, reason: str = None) -> ClientResponse:
        """Creates a new thread from an existing message.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to start the thread in.
        message_id : int
            The ID of the message to start the thread from.
        name : str
            1-100 character channel name.
        auto_archive_duration : int
            Duration in minutes to automatically archive the thread after recent activity.
        rate_limit_per_user : int
            Amount of seconds a user has to wait before sending another message.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            A channel object.
        """
        path = f'/channels/{channel_id}/messages/{message_id}/threads'
        bucket = 'POST' + path
        payload = {
            'name': name,
            'auto_archive_duration': auto_archive_duration,
            'rate_limit_per_user': rate_limit_per_user,
        }

        return await self._client._request('POST', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def start_thread_without_message(self, channel_id: int, name: str, auto_archive_duration: int, type: int, invitable: bool = True, rate_limit_per_user: int = None, reason: str = None) -> ClientResponse:
        """Creates a new thread.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to start the thread in.
        name : str
            1-100 character channel name.
        auto_archive_duration : int
            Duration in minutes to automatically archive the thread after recent activity.
        type : int
            The type of thread to create.
        invitable : bool, optional
            Whether non-moderators can add other non-moderators to a thread, by default True
        rate_limit_per_user : int, optional
            Amount of seconds a user has to wait before sending another message, by default None
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            A channel object.
        """
        path = f'/channels/{channel_id}/threads'
        bucket = 'POST' + path
        payload = {
            'name': name,
            'auto_archive_duration': auto_archive_duration,
            'type': type,
            'invitable': invitable,
            'rate_limit_per_user': rate_limit_per_user,
        }

        return await self._client._request('POST', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def start_thread_in_forum(self, channel_id: int, name: str, auto_archive_duration: int, rate_limit_per_user: int = None, reason: str = None, **message: Any) -> ClientResponse:
        """Creates a new thread in a forum channel.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to start the thread in.
        name : str
            1-100 character channel name.
        auto_archive_duration : int
            Duration in minutes to automatically archive the thread after recent activity.
        rate_limit_per_user : int, optional
            Amount of seconds a user has to wait before sending another message (0-21600), by default None
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None
        message : Any
            Params for a message to send in the thread.

        Returns
        -------
        ClientResponse
            A channel object, with a nested message object.

        Raises
        ------
        InvalidParams
            Invalid params were given.
        """
        path = f'/channels/{channel_id}/threads'
        bucket = 'POST' + path
        if message.get('content') is None and message.get('embeds') is None and message.get('sticker_ids') is None:
            raise InvalidParams('content, embeds or sticker_ids must be provided for the message')
        elif auto_archive_duration == 60 or auto_archive_duration == 1440 or auto_archive_duration == 4320 or auto_archive_duration == 10080:
            raise InvalidParams('auto_archive_duration must equal to 60, 1440, 4320 or 10080')
        elif 0 > rate_limit_per_user or rate_limit_per_user > 21600:
            raise InvalidParams('rate_limit_per_user must be between 0 and 21600')
        valid_message_keys = (
            'content',
            'embeds',
            'allowed_mentions',
            'components',
            'sticker_ids',
        )
        payload = {
            'name': name[:100],
            'auto_archive_duration': auto_archive_duration,
            'rate_limit_per_user': rate_limit_per_user,
        }
        payload['message'] = {k: v for k, v in message.items() if k in valid_message_keys}
        return await self._client._request('POST', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def join_thread(self, channel_id: int) -> ClientResponse:
        """Adds the current user to a thread.

        Parameters
        ----------
        channel_id : int
            The ID of the thread to join.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/thread-members/@me'
        bucket = 'PUT' + path
        return await self._client._request('PUT', path, bucket)

    async def add_user_to_thread(self, channel_id: int, user_id: int) -> ClientResponse:
        """Adds another member to a thread.

        Parameters
        ----------
        channel_id : int
            The ID of the thread to add a user to.
        user_id : int
            The ID of the user to add to the thread.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/thread-members/{user_id}'
        bucket = 'PUT' + path
        return await self._client._request('PUT', path, bucket)

    async def leave_thread(self, channel_id: int) -> ClientResponse:
        """Removes the current user from a thread.

        Parameters
        ----------
        channel_id : int
            The ID of the thread to leave.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/thread-members/@me'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket)

    async def remove_user_from_thread(self, channel_id: int, user_id: int) -> ClientResponse:
        """Removes a member from a thread.

        Parameters
        ----------
        channel_id : int
            The ID of the thread to remove a user from.
        user_id : int
            The ID of the user to remove from the thread.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/channels/{channel_id}/thread-members/{user_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket)

    async def get_thread_member(self, channel_id: int, user_id: int) -> ClientResponse:
        """Gets a thread member.

        Parameters
        ----------
        channel_id : int
            The ID of the thread to get a member from.
        user_id : int
            The ID of the user to get from the thread.

        Returns
        -------
        ClientResponse
            A thread member object.
        """
        path = f'/channels/{channel_id}/thread-members/{user_id}'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def get_thread_members(self, channel_id: int) -> ClientResponse:
        """Gets all thread members.

        Parameters
        ----------
        channel_id : int
            The ID of the thread to get members from.

        Returns
        -------
        ClientResponse
            A list of thread member objects.
        """
        path = f'/channels/{channel_id}/thread-members'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def get_public_archived_threads(self, channel_id: int, before: ISO8601_timestamp = None, limit: int = 50) -> ClientResponse:
        """Returns archived threads in the channel that are public.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to get archived threads from.
        before : ISO8601_timestamp, optional
            Returns threads before this timestamp, by default None
        limit : int, optional
            Optional maximum number of threads to return, by default 50

        Returns
        -------
        ClientResponse
            A list of archived threads in the channel that are public.
        """
        path = f'/channels/{channel_id}/threads/archived/public'
        bucket = 'GET' + path

        params = {}
        if before:
            params['before'] = before
        params['limit'] = limit
        return await self._client._request('GET', path, bucket, params=params)

    async def get_private_archived_threads(self, channel_id: int, before: ISO8601_timestamp = None, limit = 50) -> ClientResponse:
        """Returns archived threads in the channel that are private.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to get archived threads from.
        before : ISO8601_timestamp, optional
            Returns threads before this timestamp, by default None
        limit : int, optional
            Optional maximum number of threads to return, by default 50

        Returns
        -------
        ClientResponse
            A list of archived threads in the channel that are private.
        """
        path = f'/channels/{channel_id}/threads/archived/private'
        bucket = 'GET' + path

        params = {}
        if before:
            params['before'] = before
        params['limit'] = limit
        return await self._client._request('GET', path, bucket, params=params)

    async def get_joined_private_archived_threads(self, channel_id: int, before: int = None, limit: int = 50) -> ClientResponse:
        """Returns archived joined threads in the channel that are private.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to get joined archived threads from.
        before : int, optional
            Returns threads before this id, by default None
        limit : int, optional
            Optional maximum number of threads to return, by default 50

        Returns
        -------
        ClientResponse
            A list of archived joined threads in the channel that are private.
        """
        path = f'/channels/{channel_id}/users/@me/threads/archived/private'
        bucket = 'GET' + path
        params = {}
        if before:
            params['before'] = before
        params['limit'] = limit
        return await self._client._request('GET', path, bucket, params=params)

    """
    Emoji
    """

    async def get_guild_emojis(self, guild_id: int) -> ClientResponse:
        """Gets all emojis in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get emojis from.

        Returns
        -------
        ClientResponse
            A list of emoji objects.
        """
        path = f'/guilds/{guild_id}/emojis'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def get_guild_emoji(self, guild_id: int, emoji_id: int) -> ClientResponse:
        """Gets an emoji in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get an emoji from.
        emoji_id : int
            The ID of the emoji to get.

        Returns
        -------
        ClientResponse
            An emoji object.
        """
        path = f'/guilds/{guild_id}/emojis/{emoji_id}'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    """
    async def create_guild_emoji(self, guild_id: int, name, image, *, roles = None, reason: str = None) -> ClientResponse:
        payload = {
            'name': name,
            'image': image,
            'roles': roles or [],
        }

        r = Route('POST', '/guilds/{guild_id}/emojis', guild_id=guild_id: int)
        return await self._client._request(r, json=payload, reason=reason)
    """

    async def edit_custom_emoji(self, guild_id: int, emoji_id: int, name: str = None, roles: List[int] = None, reason: str = None) -> ClientResponse:
        """Edits a custom emoji.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to edit an emoji from.
        emoji_id : int
            The ID of the emoji to edit.
        name : str, optional
            Name of the emoji, by default None
        roles : List[int], optional
            A Llst of roles allowed to use this emoji, by default None
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            An emoji object.
        """
        path = f'/guilds/{guild_id}/emojis/{emoji_id}'
        bucket = 'PATCH' + path
        payload = {}
        if name is not None:
            payload['name'] = name
        if roles is not None:
            payload['roles'] = roles
        return await self._client._request('PATCH', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def delete_custom_emoji(self, guild_id: int, emoji_id: int, reason: str = None) -> ClientResponse:
        """Deletes a custom emoji.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to delete an emoji from.
        emoji_id : int
            The ID of the emoji to delete.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/emojis/{emoji_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    """
    Guild
    """

    async def create_guild(self, name: str, verification_level: int = None, default_message_notifications: int = None, explicit_content_filter: int = None, roles: List[Any] = None, channels: List[Any] = None, afk_channel_id: int = None, afk_timeout:int = None, system_channel_id: int = None, system_channel_flags: int = None) -> ClientResponse:
        """Create a new guild.

        Parameters
        ----------
        name : str
            Name of the guild (2-100 characters).
        verification_level : int, optional
            The verification level for the guild, by default None
        default_message_notifications : int, optional
            The default message notification level, by default None
        explicit_content_filter : int, optional
            The explicit content filter level, by default None
        roles : List[Any], optional
            The roles for the guild, by default None
        channels : List[Any], optional
            The channels for the guild, by default None
        afk_channel_id : int, optional
            The ID for afk channel, by default None
        afk_timeout : int, optional
            The AFK timeout in seconds, by default None
        system_channel_id : int, optional
            The id of the channel where guild notices are sent, by default None
        system_channel_flags : int, optional
            System channel flags, by default None

        Returns
        -------
        ClientResponse
            A guild object.
        """
        path = '/guilds'
        bucket = 'POST' + path
        payload = {
            'name': name,
        }
        if verification_level is not None:
            payload['verification_level'] = verification_level
        if default_message_notifications is not None:
            payload['default_message_notifications'] = default_message_notifications
        if explicit_content_filter is not None:
            payload['explicit_content_filter'] = explicit_content_filter
        if roles is not None:
            payload['roles'] = roles
        if channels is not None:
            payload['channels'] = channels
        if afk_channel_id is not None:
            payload['afk_channel_id'] = afk_channel_id
        if afk_timeout is not None:
            payload['afk_timeout'] = afk_timeout
        if system_channel_id is not None:
            payload['system_channel_id'] = system_channel_id
        if system_channel_flags is not None:
            payload['system_channel_flags'] = system_channel_flags

        return await self._client._request('POST', path, bucket, json=payload)

    async def get_guild(self, guild_id: int, with_counts: bool = True) -> ClientResponse:
        """Get a guild by ID.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get.
        with_counts : bool, optional
            When true, will return approximate member and presence counts for the guild, by default True

        Returns
        -------
        ClientResponse
            A guild object.
        """
        path = f'/guilds/{guild_id}'
        bucket = 'GET' + path
        params = {'with_counts': with_counts}
        return await self._client._request('GET', path, bucket, params=params)

    async def get_guild_preview(self, guild_id: int) -> ClientResponse:
        """Get a guild preview by ID.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get.

        Returns
        -------
        ClientResponse
            A guild preview object.
        """
        path = f'/guilds/{guild_id}/preview'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def edit_guild(self, guild_id: int, reason: str = None, **options: Any) -> ClientResponse:
        """Edit a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to edit.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None
        options : Any
            The params required to update the required aspects of the guild.

        Returns
        -------
        ClientResponse
            A guild object.
        """
        path = f'/guilds/{guild_id}'
        bucket = 'PATCH' + path

        payload = {}

        valid_keys = (
            'name',
            'region',
            'verification_level',
            'default_message_notifications',
            'explicit_content_filter',
            'afk_channel_id',
            'afk_timeout',
            'owner_id',
            'system_channel_id',
            'system_channel_flags',
            'rules_channel_id',
            'public_updates_channel_id',
            'preferred_locale',
            'features',
            'description',
            'premium_progress_bar_enabled',
        )
        payload.update({k: v for k, v in options.items() if k in valid_keys and v is not None})

        self._request('PATCH', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def delete_guild(self, guild_id: int) -> ClientResponse:
        """Delete a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to delete.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket)

    async def get_guild_channels(self, guild_id: int) -> ClientResponse:
        """Get a guild's channels.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get channels for.

        Returns
        -------
        ClientResponse
            A list of guild channel objects.
        """
        path = f'/guilds/{guild_id}/channels'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def create_channel(self, guild_id: int, name: str, *, reason: str = None, **options: Any) -> ClientResponse:
        """Create a channel in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to create a channel in.
        name : str
            The channel name (1-100 characters).
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None
        options : Any
            The params required to create a channel of the required settings.

        Returns
        -------
        ClientResponse
            A channel object.
        """
        path = f'/guilds/{guild_id}/channels'
        bucket = 'POST' + path

        payload = {
            'name': name,
        }

        valid_keys = (
            'type',
            'topic',
            'bitrate',
            'user_limit',
            'rate_limit_per_user',
            'position',
            'permission_overwrites',
            'parent_id',
            'nsfw',
            'default_auto_archive_duration',
        )
        payload.update({k: v for k, v in options.items() if k in valid_keys and v is not None})

        return await self._client._request('POST', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def edit_channel_position(self, guild_id: int, channel_id: int, position: int, sync_permissions: bool, parent_id: int, reason: str = None) -> ClientResponse:
        """Edit a channel's position in the channel list.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to edit the channel position in.
        channel_id : int
            The ID of the channel to edit.
        position : int
            The new position of the channel.
        sync_permissions : bool
            Whether to sync permissions with the channel's new position.
        parent_id : int
            The ID of the new parent category for the channel.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/channels'
        bucket = 'PATCH' + path

        payload = {
            'id': channel_id,
            'position': position,
            'lock_permissions': sync_permissions,
            'parent_id': parent_id
        }

        return await self._client._request('PATCH', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def get_active_threads(self, guild_id: int) -> ClientResponse:
        """Get a guild's active threads.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get active threads for.

        Returns
        -------
        ClientResponse
            A list of threads and members.
        """
        path = f'/guilds/{guild_id}/threads/active'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def get_member(self, guild_id: int, member_id: int) -> ClientResponse:
        """Get a member in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get a member from.
        member_id : int
            The ID of the member to get.

        Returns
        -------
        ClientResponse
            A guild member object.
        """
        path = f'/guilds/{guild_id}/members/{member_id}'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def get_members(self, guild_id: int, limit: int = 1, after: int = None) -> ClientResponse:
        """Get a list of members in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get members from.
        limit : int, optional
            Max number of members to return (1-1000), by default 1
        after : int, optional
            The highest user id in the previous page, by default None

        Returns
        -------
        ClientResponse
            A list of guild member objects.

        Raises
        ------
        InvalidParams
            If the limit is not between 1 and 1000.
        """
        if 1 > limit or limit > 1000:
            raise InvalidParams('limit must be between 1 and 1000')

        path = f'/guilds/{guild_id}/members'
        bucket = 'GET' + path

        params = {
            'limit': limit,
        }
        if after is not None:
            params['after'] = after

        return await self._client._request('GET', path, bucket, params=params)

    async def search_guild_members(self, guild_id: int, query: str, limit: int = 1) -> ClientResponse:
        """Search for members in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to search for members in.
        query : str
            The query to search for.
        limit : int, optional
            Max number of members to return (1-1000), by default 1

        Returns
        -------
        ClientResponse
            A list of guild member objects.

        Raises
        ------
        InvalidParams
            If the limit is not between 1 and 1000.
        """
        if 1 > limit or limit > 1000:
            raise InvalidParams('limit must be between 1 and 1000')

        path = f'/guilds/{guild_id}/members/search'
        bucket = 'GET' + path

        params = {
            'limit': limit,
            'query': query,
        }
        return await self._client._request('GET', path, bucket, params=params)

    async def add_guild_member(self, guild_id: int, user_id: int, access_token: str, nick: str = None, roles: List[int] = None, mute: bool = False, deaf: bool = False) -> ClientResponse:
        """Add a member to a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to add a member to.
        user_id : int
            The ID of the user to add.
        access_token : str
            The access token of the user to add.
        nick : str, optional
            Value to set user's nickname to, by default None
        roles : List[int], optional
            Array of role ids the member is assigned, by default None
        mute : bool, optional
            Whether the user is muted in voice channels, by default False
        deaf : bool, optional
            Whether the user is deafened in voice channels, by default False

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/members/{user_id}'
        bucket = 'PUT' + path

        payload = {
            'access_token': access_token,
            'mute': mute,
            'deaf': deaf
        }

        if nick is not None:
            payload['nick'] = nick
        if roles is not None:
            payload['roles'] = roles

        return await self._client._request('PUT', path, bucket, json=payload)

    async def modify_guild_member(self, user_id: int, guild_id: int, nick: str = None, roles: List[int] = None, mute: bool = None, deafen: bool = None, channel_id: int = None, timeout: ISO8601_timestamp = None, reason: str = None) -> ClientResponse:
        """Modify a member in a guild.

        Parameters
        ----------
        user_id : int
            The ID of the user to modify.
        guild_id : int
            The ID of the guild to modify the member in.
        nick : str, optional
            Value to set user's nickname to, by default None
        roles : List[int], optional
            Array of role ids the member is assigned, by default None
        mute : bool, optional
            Whether the user is muted in voice channels, by default None
        deafen : bool, optional
            Whether the user is deafened in voice channels, by default None
        channel_id : int, optional
            ID of channel to move user to, by default None
        timeout : ISO8601_timestamp, optional
            When the user's timeout will expire and the user will be able to communicate in the guild again, by default None
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/members/{user_id}'
        bucket = 'PATCH' + path
        payload = {}
        if nick is not None:
            payload['nick'] = nick
        if roles is not None:
            payload['roles'] = roles
        if mute is not None:
            payload['mute'] = mute
        if deafen is not None:
            payload['deaf'] = deafen
        if channel_id is not None:
            payload['channel_id'] = channel_id
        if timeout is not None:
            payload['timeout'] = timeout

        return await self._client._request('PATCH', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def modify_current_member(self, guild_id: int, nick: str, reason: str = None) -> ClientResponse:
        """Modify the current user in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to modify the member in.
        nick : str
            Value to set user's nickname to.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/members/@me'
        bucket = 'PATCH' + path
        payload = {
            'nick': nick
        }
        return await self._client._request('PATCH', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def add_role(self, guild_id: int, user_id: int, role_id: int, reason: str = None) -> ClientResponse:
        """Add a role to a member in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild that the users is in.
        user_id : int
            The ID of the user to add a role to.
        role_id : int
            The ID of the role to add.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/members/{user_id}/roles/{role_id}'
        bucket = 'PUT' + path
        return await self._client._request('PUT', path, bucket, headers={'X-Audit-Log-Reason': reason})

    async def remove_role(self, guild_id: int, user_id: int, role_id: int, reason: str = None) -> ClientResponse:
        """Remove a role from a member in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild that the users is in.
        user_id : int
            The ID of the user to remove a role from.
        role_id : int
            The ID of the role to remove.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/members/{user_id}/roles/{role_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    async def kick(self, user_id: int, guild_id: int, reason: str = None) -> ClientResponse:
        """Kick a member from a guild.

        Parameters
        ----------
        user_id : int
            The ID of the user to kick.
        guild_id : int
            The ID of the guild to kick the member from.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/members/{user_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    async def get_bans(self, guild_id: int, limit: int = 1000, before: int = None, after: int = None) -> ClientResponse:
        """Get a list of all bans in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get bans from.
        limit : int, optional
            The number of users to return (up to maximum 1000), by default 1000
        before : int, optional
            Consider only users before given user id, by default None
        after : int, optional
            Consider only users after given user id, by default None

        Returns
        -------
        ClientResponse
            A list of ban objects.
        """
        path = f'/guilds/{guild_id}/bans'
        bucket = 'GET' + path
        params = {
            'limit': limit,
        }
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after

        return await self._client._request('GET', path, bucket, params=params)

    async def get_ban(self, user_id: int, guild_id: int) -> ClientResponse:
        """Get a ban from a guild.

        Parameters
        ----------
        user_id : int
            The ID of the user to get a ban from.
        guild_id : int
            The ID of the guild to get a ban from.

        Returns
        -------
        ClientResponse
            A ban object.
        """
        path = f'/guilds/{guild_id}/bans/{user_id}'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def ban(self, user_id: int, guild_id: int, delete_message_days: int = 0, reason: str = None) -> ClientResponse:
        """Ban a user from a guild.

        Parameters
        ----------
        user_id : int
            The ID of the user to ban.
        guild_id : int
            The ID of the guild to ban the user from.
        delete_message_days : int, optional
            Number of days to delete messages for (0-7), by default 0
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            A ban object.

        Raises
        ------
        InvalidParams
            If the delete_message_days is not an integer between 0 and 7.
        """
        if 0 > delete_message_days or delete_message_days > 7:
            raise InvalidParams('limit must be between 0 and 7')

        path = f'/guilds/{guild_id}/bans/{user_id}'
        bucket = 'PUT' + path

        params = {
            'delete_message_days': delete_message_days,
        }

        return await self._client._request('PUT', path, bucket, params=params, headers={'X-Audit-Log-Reason': reason})

    async def unban(self, user_id: int, guild_id: int, *, reason: str = None) -> ClientResponse:
        """Unban a user from a guild.

        Parameters
        ----------
        user_id : int
            The ID of the user to unban.
        guild_id : int
            The ID of the guild to unban the user from.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/bans/{user_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    async def get_roles(self, guild_id: int) -> ClientResponse:
        """Get a list of all roles in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get roles from.

        Returns
        -------
        ClientResponse
            A list of role objects.
        """
        path = f'/guilds/{guild_id}/roles'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def create_role(self, guild_id: int, name: str = None, permissions: str = None, colour: int = None, hoist: bool = None, unicode_emoji: str = None, mentionable: bool = None, reason: str = None) -> ClientResponse:
        """Create a role in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to create a role in.
        name : str, optional
            Name of the role, by default None
        permissions : str, optional
            Bitwise value of the enabled permissions, by default None
        colour : int, optional
            RGB colour value, by default None
        hoist : bool, optional
            Whether the role should be displayed separately in the sidebar, by default None
        unicode_emoji : str, optional
            The role's unicode emoji as a standard emoji, by default None
        mentionable : bool, optional
            Whether the role should be mentionable, by default None
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            A role object.
        """
        path = f'/guilds/{guild_id}/roles'
        bucket = 'POST' + path
        payload = {}
        if name is not None:
            payload['name'] = name
        if permissions is not None:
            payload['permissions'] = permissions
        if colour is not None:
            payload['color'] = colour
        if hoist is not None:
            payload['hoist'] = hoist
        if unicode_emoji is not None:
            payload['unicode_emoji'] = unicode_emoji
        if mentionable is not None:
            payload['mentionable'] = mentionable
        return await self._client._request('POST', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def move_role_position(self, guild_id: int, role_id: int, position: int, reason: str = None) -> ClientResponse:
        """Move a role's position in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to move a role in.
        role_id : int
            The ID of the role to move.
        position : int
            The new position of the role.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            A list of role objects.
        """
        path = f'/guilds/{guild_id}/roles'
        bucket = 'PATCH' + path
        payload = {
            'id': role_id,
            'position': position
        }
        return await self._client._request('PATCH', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def edit_role(self, guild_id: int, role_id: int, reason: str = None, **fields: Any) -> ClientResponse:
        """Edit a role in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to edit a role in.
        role_id : int
            The ID of the role to edit.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None
        **fields : Any
            The params required to update the required aspects of the role.

        Returns
        -------
        ClientResponse
            A role object.
        """
        path = f'/guilds/{guild_id}/roles/{role_id}'
        bucket = 'PATCH' + path
        valid_keys = ('name', 'permissions', 'color', 'hoist', 'unicode_emoji', 'mentionable')
        payload = {k: v for k, v in fields.items() if k in valid_keys}
        return await self._client._request('PATCH', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def delete_role(self, guild_id: int, role_id: int, reason: str = None) -> ClientResponse:
        """Delete a role from a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to delete a role from.
        role_id : int
            The ID of the role to delete.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/roles/{role_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    async def estimate_pruned_members(self, guild_id: int, days: int = 7, roles: str = None) -> ClientResponse:
        """Get the number of members that would be removed from a guild if prune was run.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get prune estimates for.
        days : int, optional
            Number of days to count prune for (1-30), by default 7
        roles : str, optional
            Role(s) to include, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.

        Raises
        ------
        InvalidParams
            If the days parameter is not between 1 and 30.
        """
        if 1 > days or days > 30:
            raise InvalidParams('days must be between 1 and 30')

        path = f'/guilds/{guild_id}/prune'
        bucket = 'GET' + path

        params = {
            'days': days,
        }
        if roles is not None:
            params['include_roles'] = ', '.join(roles)

        return await self._client._request('GET', path, bucket, params=params)

    async def prune_members(self, guild_id: int, days: int = 7, compute_prune_count: bool = False, roles: List[int] = None, reason: str = None) -> ClientResponse:
        """Prune members from a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to prune members from.
        days : int, optional
            Number of days to prune (1-30), by default 7
        compute_prune_count : bool, optional
            Whether pruned is returned, by default False
        roles : List[int], optional
            Role(s) to include, by default None
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.

        Raises
        ------
        InvalidParams
            If the days parameter is not between 1 and 30.
        """
        if 1 > days or days > 30:
            raise InvalidParams('days must be between 1 and 30')

        path = f'/guilds/{guild_id}/prune'
        bucket = 'POST' + path

        payload = {
            'days': days,
            'compute_prune_count': compute_prune_count,
        }
        if roles:
            payload['include_roles'] = ', '.join(roles)

        return await self._client._request('POST', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def get_voice_regions(self, guild_id: int) -> ClientResponse:
        """Get the voice regions for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get voice regions for.

        Returns
        -------
        ClientResponse
            A list of voice region objects.
        """
        path = f'/guilds/{guild_id}/regions'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def get_guild_invites(self, guild_id: int) -> ClientResponse:
        """Get the invites for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get invites for.

        Returns
        -------
        ClientResponse
            A list of invite objects.
        """
        path = f'/guilds/{guild_id}/invites'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def get_guild_integrations(self, guild_id: int) -> ClientResponse:
        """Get the integrations for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get integrations for.

        Returns
        -------
        ClientResponse
            A list of integration objects.
        """
        path = f'/guilds/{guild_id}/integrations'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def create_integration(self, guild_id: int, type: Any, id: Any) -> ClientResponse:
        """Create an integration for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to create an integration for.
        type : Any
            The type of integration to create.
        id : Any
            The ID of the integration to create.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/integrations'
        bucket = 'POST' + path

        payload = {
            'type': type,
            'id': id,
        }

        return await self._client._request('POST', path, bucket, json=payload)

    async def edit_integration(self, guild_id: int, integration_id: int, **payload : Any) -> ClientResponse:
        """Edit an integration for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to edit an integration for.
        integration_id : int
            The ID of the integration to edit.
        payload : Any
            The params for the JSON payload.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/integrations/{integration_id}'
        bucket = 'PATCH' + path

        return await self._client._request('PATCH', path, bucket, json=payload)

    async def sync_integration(self, guild_id: int, integration_id: int) -> ClientResponse:
        """Sync an integration for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to sync an integration for.
        integration_id : int
            The ID of the integration to sync.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/integrations/{integration_id}/sync'
        bucket = 'POST' + path

        return await self._client._request('POST', path, bucket)

    async def delete_guild_integration(self, guild_id: int, integration_id: int, *, reason: str = None) -> ClientResponse:
        """Delete an integration for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to delete an integration for.
        integration_id : int
            The ID of the integration to delete.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/integrations/{integration_id}'
        bucket = 'DELETE' + path

        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    async def get_guild_widget_settings(self, guild_id: int) -> ClientResponse:
        """Get the widget settings for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get widget settings for.

        Returns
        -------
        ClientResponse
            A guild widget settings object.
        """
        path = f'/guilds/{guild_id}/widget'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def edit_widget(self, guild_id: int, enabled, channel_id: int, reason: str = None) -> ClientResponse:
        """Edit the widget settings for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to edit widget settings for.
        enabled : _type_
            Whether the widget is enabled.
        channel_id : int
            The ID of the channel to send the widget to.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            A guild widget settings object.
        """
        path = f'/guilds/{guild_id}/widget'
        bucket = 'PATCH' + path
        payload = {
            'enabled': enabled,
            'channel_id': channel_id,
        }
        return await self._client._request('PATCH', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def get_guild_widget(self, guild_id: int) -> ClientResponse:
        """Get the widget for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get widget for.

        Returns
        -------
        ClientResponse
            A guild widget object.
        """
        path = f'/guilds/{guild_id}/widget.json'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def get_vanity_code(self, guild_id: int) -> ClientResponse:
        """Get the vanity URL for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get the vanity URL for.

        Returns
        -------
        ClientResponse
            A partial invite object.
        """
        path = f'/guilds/{guild_id}/vanity-url'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def change_vanity_code(self, guild_id: int, code, reason: str = None) -> ClientResponse:
        """Change the vanity URL for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to change the vanity URL for.
        code : _type_
            The vanity URL code.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/vanity-url'
        bucket = 'PATCH' + path
        payload = {'code': code}
        return await self._client._request('PATCH', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def get_guild_welcome_screen(self, guild_id: int) -> ClientResponse:
        """Get the welcome screen for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get the welcome screen for.

        Returns
        -------
        ClientResponse
            A welcome screen object.
        """
        path = f'/guilds/{guild_id}/welcome-screen'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def edit_guild_welcome_screen(self, guild_id: int, enabled: bool = None, welcome_channels: List[Any] = None, description: str = None, reason: str = None) -> ClientResponse:
        """Edit the welcome screen for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to edit the welcome screen for.
        enabled : bool, optional
            Whether the welcome screen is enabled, by default None
        welcome_channels : List[Any], optional
            Channels linked in the welcome screen and their display options, by default None
        description : str, optional
            The server description to show in the welcome screen, by default None
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            A welcome screen object.
        """
        path = f'/guilds/{guild_id}/welcome-screen'
        bucket = 'PATCH' + path

        payload = {
            'enabled': enabled,
            'welcome_channels': welcome_channels,
            'description': description
        }

        return await self._client._request('PATCH', path, bucket, json=payload, header={'X-Audit-Log-Reason': reason})

    async def edit_voice_state(self, guild_id: int, channel_id: int, suppress: bool = None, request_to_speak_timestamp: ISO8601_timestamp = None) -> ClientResponse:
        """Edit the voice state for a user.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to edit the voice state for.
        channel_id : int
            The id of the channel the user is currently in.
        suppress : bool, optional
            Toggles the user's suppress state, by default None
        request_to_speak_timestamp : ISO8601_timestamp, optional
            Sets the user's request to speak, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/voice-states/@me'
        bucket = 'PATCH' + path
        payload = {
            'channel_id': channel_id,
        }
        if suppress is not None:
            payload['suppress'] = suppress
        if request_to_speak_timestamp is not None:
            payload['request_to_speak_timestamp'] = request_to_speak_timestamp
        return await self._client._request('PATCH', path, bucket, json=payload)

    async def edit_users_voice_state(self, guild_id: int, user_id: int, channel_id: int, suppress: bool = None) -> ClientResponse:
        """Edit the voice state for a user.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to edit the voice state for.
        user_id : int
            The ID of the user to edit the voice state for.
        channel_id : int
            The id of the channel the user is currently in
        suppress : bool, optional
            Toggles the user's suppress state, by default None

        Returns
        -------
        ClientResponse
            _description_
        """
        path = f'/guilds/{guild_id}/voice-states/{user_id}'
        bucket = 'PATCH' + path
        payload = {
            'channel_id': channel_id,
        }
        if suppress is not None:
            payload['suppress'] = suppress
        return await self._client._request('PATCH', path, bucket, json=payload)

    """
    Guild Scheduled Event
    """

    async def get_scheduled_events(self, guild_id: int, with_user_count: bool) -> ClientResponse:
        """Get the scheduled events for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get the scheduled events for.
        with_user_count : bool
            Include number of users subscribed to each event.

        Returns
        -------
        ClientResponse
            A list of guild scheduled event objects.
        """
        path = f'/guilds/{guild_id}/scheduled-events'
        bucket = 'GET' + path
        params = {'with_user_count': with_user_count}
        return await self._client._request('GET', path, bucket, params=params)

    async def create_guild_scheduled_event(self, guild_id: int, reason: str = None, **payload: Any) -> ClientResponse:
        """Create a scheduled event for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to create the scheduled event for.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None
        payload : Any
            The params for the JSON payload.

        Returns
        -------
        ClientResponse
            A guild scheduled event object.
        """
        path = f'/guilds/{guild_id}/scheduled-events'
        bucket = 'POST' + path
        valid_keys = (
            'channel_id',
            'entity_metadata',
            'name',
            'privacy_level',
            'scheduled_start_time',
            'scheduled_end_time',
            'description',
            'entity_type',
            'image',
        )
        payload = {k: v for k, v in payload.items() if k in valid_keys}

        return await self._client._request('POST', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def get_scheduled_event(self, guild_id: int, guild_scheduled_event_id: int, with_user_count: bool) -> ClientResponse:
        """Get a scheduled event for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get the scheduled event for.
        guild_scheduled_event_id : int
            The ID of the scheduled event to get.
        with_user_count : bool
            Include number of users subscribed to this event.

        Returns
        -------
        ClientResponse
            A guild scheduled event object.
        """
        path = f'/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}'
        bucket = 'GET' + path
        params = {'with_user_count': with_user_count}
        return await self._client._request('GET', path, bucket, params=params)

    async def edit_scheduled_event(self, guild_id: int, guild_scheduled_event_id: int, *, reason: str = None, **payload: Any) -> ClientResponse:
        """Edit a scheduled event for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to edit the scheduled event for.
        guild_scheduled_event_id : int
            The ID of the scheduled event to edit.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None
        payload : Any
            The params required to update the required aspects of the scheduled event.

        Returns
        -------
        ClientResponse
            A guild scheduled event object.
        """
        path = f'/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}'
        bucket = 'PATCH' + path
        valid_keys = (
            'channel_id',
            'entity_metadata',
            'name',
            'privacy_level',
            'scheduled_start_time',
            'scheduled_end_time',
            'status',
            'description',
            'entity_type',
            'image',
        )
        payload = {k: v for k, v in payload.items() if k in valid_keys}

        return await self._client._request('PATCH', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def delete_scheduled_event(self, guild_id: int, guild_scheduled_event_id: int, reason: str = None) -> ClientResponse:
        """Delete a scheduled event for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to delete the scheduled event for.
        guild_scheduled_event_id : int
            The ID of the scheduled event to delete.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    async def get_scheduled_event_users(self, guild_id: int, guild_scheduled_event_id: int, limit: int, with_member: bool, before: int = None, after: int = None) -> ClientResponse:
        """Get the users subscribed to a scheduled event.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get the scheduled event users for.
        guild_scheduled_event_id : int
            The ID of the scheduled event to get the users for.
        limit : int
            Number of users to return (up to maximum 100)
        with_member : bool
            Include guild member data if it exists
        before : int, optional
            Consider only users before given user id, by default None
        after : int, optional
            Consider only users after given user id, by default None

        Returns
        -------
        ClientResponse
            A list of guild scheduled event user objects.
        """
        path = f'/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}/users'
        bucket = 'GET' + path

        params = {
            'limit': limit,
            'with_member': int(with_member),
        }

        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after

        return await self._client._request('GET', path, bucket, params=params)

    """
    Guild Template
    """

    async def get_template(self, code: str) -> ClientResponse:
        """Get a guild template.

        Parameters
        ----------
        code : str
            The code of the template to get.

        Returns
        -------
        ClientResponse
            A guild template object.
        """
        path = f'/guilds/templates/{code}'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def create_from_template(self, code: str, name: str) -> ClientResponse:
        """Create a guild from a template.

        Parameters
        ----------
        code : str
            The code of the template to create the guild from.
        name : str
            Name of the guild (2-100 characters).

        Returns
        -------
        ClientResponse
            A guild object.
        """
        path = f'/guilds/templates/{code}'
        bucket = 'POST' + path
        payload = {
            'name': name,
        }
        return await self._client._request('POST', path, bucket, json=payload)

    async def get_guild_templates(self, guild_id: int) -> ClientResponse:
        """Get a guild's templates.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get the templates for.

        Returns
        -------
        ClientResponse
            A list of guild template objects.
        """
        path = f'/guilds/{guild_id}/templates'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def create_template(self, guild_id: int, name: str, description: str = None) -> ClientResponse:
        """Create a template for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to create the template for.
        name : str
            Name of the template (1-100 characters).
        description : str, optional
            Description for the template (0-120 characters), by default None

        Returns
        -------
        ClientResponse
            A guild template object.
        """
        path = f'/guilds/{guild_id}/templates'
        bucket = 'POST' + path
        payload = {
            'name': name[:100],
        }
        if description is not None:
            payload['description'] = description[:120]
        return await self._client._request('POST', path, bucket, json=payload)

    async def sync_template(self, guild_id: int, code: str) -> ClientResponse:
        """Sync a template for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to sync the template for.
        code : str
            The code of the template to sync.

        Returns
        -------
        ClientResponse
            A guild template object.
        """
        path = f'/guilds/{guild_id}/templates/{code}'
        bucket = 'PUT' + path
        return await self._client._request('PUT', path, bucket)

    async def edit_template(self, guild_id: int, code: str, name: str, description: str = None) -> ClientResponse:
        """Edit a template for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to edit the template for.
        code : str
            The code of the template to edit.
        name : str
            Name of the template (1-100 characters)
        description : str, optional
            Description for the template (0-120 characters), by default None

        Returns
        -------
        ClientResponse
            A guild template object.
        """
        path = f'/guilds/{guild_id}/templates/{code}'
        bucket = 'PATCH' + path
        payload = {
            'name': name[:100],
        }
        if description is not None:
            payload['description'] = description[:120]
        return await self._client._request('PATCH', path, bucket, json=payload)

    async def delete_template(self, guild_id: int, code: str) -> ClientResponse:
        """Delete a template for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to delete the template for.
        code : str
            The code of the template to delete.

        Returns
        -------
        ClientResponse
            A guild template object.
        """
        path = f'/guilds/{guild_id}/templates/{code}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket)

    """
    Invite
    """

    async def get_invite(self, invite_id: str, *, with_counts: bool = True, with_expiration: bool = True, guild_scheduled_event_id: int = None) -> ClientResponse:
        """Get an invite.

        Parameters
        ----------
        invite_id : str
            The ID of the invite to get.
        with_counts : bool, optional
            Whether the invite should contain approximate member counts, by default True
        with_expiration : bool, optional
            Whether the invite should contain the expiration date, by default True
        guild_scheduled_event_id : int, optional
            The guild scheduled event to include with the invite, by default None

        Returns
        -------
        ClientResponse
            An invite object.
        """
        path = f'/invites/{invite_id}'
        bucket = 'GET' + path
        params = {
            'with_counts': with_counts,
            'with_expiration': with_expiration,
        }

        if guild_scheduled_event_id:
            params['guild_scheduled_event_id'] = guild_scheduled_event_id

        return await self._client._request('GET', path, bucket, params=params)

    async def delete_invite(self, invite_id: str, reason: str = None) -> ClientResponse:
        """Delete an invite.

        Parameters
        ----------
        invite_id : str
            The ID of the invite to delete.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            An invite object.
        """
        path = f'/invites/{invite_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    """
    Stage Instance
    """

    async def create_stage_instance(self, *, reason: str = None, **payload: Any) -> ClientResponse:
        """Create a stage instance.

        Parameters
        ----------
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None
        payload : Any
            The params for the JSON payload.

        Returns
        -------
        ClientResponse
            A stage instance object.
        """
        path = '/stage-instances'
        bucket = 'POST' + path
        valid_keys = (
            'channel_id',
            'topic',
            'privacy_level',
        )
        payload = {k: v for k, v in payload.items() if k in valid_keys}

        return await self._client._request('POST', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def get_stage_instance(self, channel_id: int) -> ClientResponse:
        """Get a stage instance.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to get the stage instance for.

        Returns
        -------
        ClientResponse
            A stage instance object.
        """
        path = f'/stage-instances/{channel_id}'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def edit_stage_instance(self, channel_id: int, *, reason: str = None, **payload: Any) -> ClientResponse:
        """Edit a stage instance.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to edit the stage instance for.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None
        payload : Any
            The params for the JSON payload.

        Returns
        -------
        ClientResponse
            A stage instance object.
        """
        path = f'/stage-instances/{channel_id}'
        bucket = 'PATCH' + path
        valid_keys = (
            'topic',
            'privacy_level',
        )
        payload = {k: v for k, v in payload.items() if k in valid_keys}

        return await self._client._request('PATCH', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def delete_stage_instance(self, channel_id: int, reason: str = None) -> ClientResponse:
        """Delete a stage instance.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to delete the stage instance for.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/stage-instances/{channel_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    """
    Sticker
    """

    async def get_sticker(self, sticker_id: int) -> ClientResponse:
        """Get a sticker.

        Parameters
        ----------
        sticker_id : int
            The ID of the sticker to get.

        Returns
        -------
        ClientResponse
            A sticker object.
        """
        path = f'/stickers/{sticker_id}'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def list_nitro_sticker_packs(self) -> ClientResponse:
        """List all nitro sticker packs.

        Returns
        -------
        ClientResponse
            A list of sticker pack objects.
        """
        path = '/sticker-packs'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def list_guild_stickers(self, guild_id: int) -> ClientResponse:
        """List all stickers in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to list stickers for.

        Returns
        -------
        ClientResponse
            A list of sticker objects.
        """
        path = f'/guilds/{guild_id}/stickers'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def get_guild_sticker(self, guild_id: int, sticker_id: int) -> ClientResponse:
        """Get a sticker in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get the sticker for.
        sticker_id : int
            The ID of the sticker to get.

        Returns
        -------
        ClientResponse
            A sticker object.
        """
        path = f'/guilds/{guild_id}/stickers/{sticker_id}'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    """
    async def create_guild_sticker(self, guild_id: int, payload, file, reason) -> ClientResponse:
        initial_bytes = file.fp.read(16)

        try:
            mime_type = _get_mime_type_for_image(initial_bytes)
        except ValueError:
            if initial_bytes.startswith(b'{') -> ClientResponse:
                mime_type = 'application/json'
            else:
                mime_type = 'application/octet-stream'
        finally:
            file.reset()

        form = [
            {
                'name': 'file',
                'value': file.fp,
                'filename': file.filename,
                'content_type': mime_type,
            }
        ]

        for k, v in payload.items() -> ClientResponse:
            form.append(
                {
                    'name': k,
                    'value': v,
                }
            )

        return await self._client._request(
            Route('POST', '/guilds/{guild_id}/stickers', guild_id=guild_id: int), form=form, files=[file], reason=reason
        )
    """

    async def modify_guild_sticker(self, guild_id: int, sticker_id: int, *, name: str = None, description: str = None, tags: str = None, reason: str = None) -> ClientResponse:
        """Modify a sticker in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to modify the sticker for.
        sticker_id : int
            The ID of the sticker to modify.
        name : str, optional
            Name of the sticker (2-30 characters), by default None
        description : str, optional
            Description of the sticker (2-100 characters), by default None
        tags : str, optional
            Autocomplete/suggestion tags for the sticker (max 200 characters), by default None
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            A sticker object.
        """
        path = f'/guilds/{guild_id}/stickers/{sticker_id}'
        bucket = 'PATCH' + path
        payload = {}
        if name is not None:
            payload['name'] = name
        if description is not None:
            payload['description'] = description
        if tags is not None:
            payload['tags'] = tags

        return await self._client._request('PATCH', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def delete_guild_sticker(self, guild_id: int, sticker_id: int, reason: str = None) -> ClientResponse:
        """Delete a sticker in a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to delete the sticker for.
        sticker_id : int
            The ID of the sticker to delete.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/guilds/{guild_id}/stickers/{sticker_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    """
    User
    """

    async def get_current_user(self) -> ClientResponse:
        """Get the current user.

        Returns
        -------
        ClientResponse
            A user object.
        """
        path = '/users/@me'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def get_user(self, user_id: int) -> ClientResponse:
        """Get a user.

        Parameters
        ----------
        user_id : int
            The ID of the user to get.

        Returns
        -------
        ClientResponse
            A user object.
        """
        path = f'/users/{user_id}'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def edit_current_user(self, username: str) -> ClientResponse:
        """Edit the current user.

        Parameters
        ----------
        username : str
            The new username.

        Returns
        -------
        ClientResponse
            A user object.
        """
        path = '/users/@me'
        bucket = 'PATCH' + path
        payload = {
            'username': username
        }
        return await self._client._request('PATCH', path, bucket, json=payload)

    async def get_current_user_guilds(self, limit: int = 200, before: int = None, after: int = None) -> ClientResponse:
        """Get the current user's guilds.

        Parameters
        ----------
        limit : int, optional
            Max number of guilds to return (1-200), by default 200
        before : int, optional
            Get guilds before this guild ID, by default None
        after : int, optional
            Get guilds after this guild ID, by default None

        Returns
        -------
        ClientResponse
            A list of partial guild objects.

        Raises
        ------
        InvalidParams
            If the limit is not between 1 and 200.
        """
        path = '/users/@me/guilds'
        bucket = 'GET' + path
        if 1 > limit or limit > 200:
            raise InvalidParams('limit must be between 1 and 200')

        params = {
            'limit': limit,
        }

        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after

        return await self._client._request('GET', path, bucket, params=params)

    async def get_current_user_guild_member(self, guild_id: int) -> ClientResponse:
        """Get the current user's guild member.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get the member for.

        Returns
        -------
        ClientResponse
            A guild member object.
        """
        path = f'/users/@me/guilds/{guild_id}/member'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def leave_guild(self, guild_id: int) -> ClientResponse:
        """Leave a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to leave.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/users/@me/guilds/{guild_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket)

    async def create_DM(self, recipient_id: int) -> ClientResponse:
        """Open a DM.

        Parameters
        ----------
        recipient_id : int
            The ID of the user to open a DM with.

        Returns
        -------
        ClientResponse
            A DM channel object.
        """
        payload = {
            'recipient_id': recipient_id,
        }
        path = f'/users/@me/channels'
        bucket = 'POST' + path

        return await self._client._request('POST', path, bucket, json=payload)

    async def create_group_DM(self, access_tokens: List[str], nicks: Dict[int, str] = None) -> ClientResponse:
        """Open a group DM.

        Parameters
        ----------
        access_tokens : List[str]
            Access tokens of users that have granted your app the gdm.join scope
        nicks : Dict[int, str], optional
            A dictionary of user ids to their respective nicknames, by default None

        Returns
        -------
        ClientResponse
            A DM channel object.
        """
        payload = {
            'access_tokens': access_tokens,
        }
        path = f'/users/@me/channels'
        bucket = 'POST' + path

        return await self._client._request('POST', path, bucket, json=payload)

    async def get_connections(self) -> ClientResponse:
        """Get the current user's connections.

        Returns
        -------
        ClientResponse
            A list of connection objects.
        """
        path = '/users/@me/connections'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    """
    Voice
    """

    async def list_voice_regions(self) -> ClientResponse:
        """Get a list of voice regions.

        Returns
        -------
        ClientResponse
            A list of voice region objects.
        """
        path = '/voice/regions'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    """
    Webhook
    """

    async def create_webhook(self, channel_id: int, name: str, reason: str = None) -> ClientResponse:
        """Create a webhook.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to create the webhook in.
        name : str
            Name of the webhook (1-80 characters).
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            A webhook object.
        """
        path = f'/channels/{channel_id}/webhooks'
        bucket = 'POST' + path
        payload = {
            'name': name,
        }

        return await self._client._request('POST', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def get_channel_webhooks(self, channel_id: int) -> ClientResponse:
        """Get a list of webhooks for a channel.

        Parameters
        ----------
        channel_id : int
            The ID of the channel to get the webhooks for.

        Returns
        -------
        ClientResponse
            A list of webhook objects.
        """
        path = f'/channels/{channel_id}/webhooks'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def get_guild_webhooks(self, guild_id: int) -> ClientResponse:
        """Get a list of webhooks for a guild.

        Parameters
        ----------
        guild_id : int
            The ID of the guild to get the webhooks for.

        Returns
        -------
        ClientResponse
            A list of webhook objects.
        """
        path = f'/guilds/{guild_id}/webhooks'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def get_webhook(self, webhook_id: int) -> ClientResponse:
        """Get a webhook.

        Parameters
        ----------
        webhook_id : int
            The ID of the webhook to get.

        Returns
        -------
        ClientResponse
            A webhook object.
        """
        path = f'/webhooks/{webhook_id}'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def get_webhook_with_token(self, webhook_id: int, webhook_token: str) -> ClientResponse:
        """Get a webhook with a token.

        Parameters
        ----------
        webhook_id : int
            The ID of the webhook to get.
        webhook_token : str
            The token of the webhook to get.

        Returns
        -------
        ClientResponse
            A webhook object.
        """
        path = f'/webhooks/{webhook_id}/{webhook_token}'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket, auth=False)

    async def edit_webhook(self, webhook_id: int, name: str = None, channel_id: int = None, reason: str = None) -> ClientResponse:
        """Edit a webhook.

        Parameters
        ----------
        webhook_id : int
            The ID of the webhook to edit.
        name : str, optional
            The default name of the webhook, by default None
        channel_id : int, optional
            The new channel id this webhook should be moved to, by default None
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            A webhook object.
        """
        path = f'/webhooks/{webhook_id}'
        bucket = 'PATCH' + path
        payload = {}
        if name is not None:
            payload['name'] = name
        if channel_id is not None:
            payload['channel_id'] = channel_id

        return await self._client._request('PATCH', path, bucket, json=payload, headers={'X-Audit-Log-Reason': reason})

    async def edit_webhook_with_token(self, webhook_id: int, webhook_token: str, name:str = None, reason: str = None) -> ClientResponse:
        """Edit a webhook with a token.

        Parameters
        ----------
        webhook_id : int
            The ID of the webhook to edit.
        webhook_token : str
            The token of the webhook to edit.
        name : str, optional
            The default name of the webhook, by default None
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            A webhook object.
        """
        path = f'/webhooks/{webhook_id}/{webhook_token}'
        bucket = 'PATCH' + path
        payload = {}

        if name is not None:
            payload['name'] = name

        return await self._client._request('PATCH', path, bucket, json=payload, auth=False, headers={'X-Audit-Log-Reason': reason})

    async def delete_webhook(self, webhook_id: int, reason: str = None) -> ClientResponse:
        """Delete a webhook.

        Parameters
        ----------
        webhook_id : int
            The ID of the webhook to delete.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/webhooks/{webhook_id}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, headers={'X-Audit-Log-Reason': reason})

    async def delete_webhook_with_token(self, webhook_id: int, webhook_token: str, reason: str = None) -> ClientResponse:
        """Delete a webhook with a token.

        Parameters
        ----------
        webhook_id : int
            The ID of the webhook to delete.
        webhook_token : str
            The token of the webhook to delete.
        reason : str, optional
            A reason for this action that will be displayed in the audit log, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/webhooks/{webhook_id}/{webhook_token}'
        bucket = 'DELETE' + path
        return await self._client._request('DELETE', path, bucket, auth=False, headers={'X-Audit-Log-Reason': reason})

    async def execute_webhook(self, webhook_id: int, webhook_token: str, wait: bool = False, thread_id: int = None, content: str = None, username: str = None, avatar_url: str = None, tts: bool = False, embeds: List[dict] = None, allowed_mentions: Any = None, components: List[Any] = None) -> ClientResponse:
        """Execute a webhook.

        Parameters
        ----------
        webhook_id : int
            The ID of the webhook to execute.
        webhook_token : str
            The token of the webhook to execute.
        wait : bool, optional
            Waits for server confirmation of message send before response, and returns the created message body, by default False
        thread_id : int, optional
            Send a message to the specified thread within a webhook's channel, by default None
        content : str, optional
            The message contents (up to 2000 characters), by default None
        username : str, optional
            Override the default username of the webhook, by default None
        avatar_url : str, optional
            Override the default avatar of the webhook, by default None
        tts : bool, optional
            True if this is a TTS message, by default False
        embeds : List[dict], optional
            Embedded rich content, by default None
        allowed_mentions : Any, optional
            Allowed mentions for the message, by default None
        components : List[Any], optional
            The components to include with the message, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.

        Raises
        ------
        InvalidParams
            If content or embeds are provided.
        """
        path = f'/webhooks/{webhook_id}/{webhook_token}'
        bucket = 'POST' + path
        if content is None and embeds is None:
            raise InvalidParams('content or embeds must be provided')

        params = {}
        if wait is not None:
            params['wait'] = wait
        if thread_id is not None:
            params['thread_id'] = thread_id

        payload = {}

        if content is not None:
            payload['content'] = content
        if username is not None:
            payload['username'] = username
        if avatar_url is not None:
            payload['avatar_url'] = avatar_url
        if tts is not None:
            payload['tts'] = tts
        if embeds is not None:
            payload['embeds'] = embeds
        if allowed_mentions is not None:
            payload['allowed_mentions'] = allowed_mentions
        if components is not None:
            payload['components'] = components

        return await self._client._request('POST', path, bucket, json=payload, params=params, auth=False)

    async def get_webhook_message(self, webhook_id: int, webhook_token: str, message_id: int, thread_id : id = None) -> ClientResponse:
        """Get a message from a webhook.

        Parameters
        ----------
        webhook_id : int
            The ID of the webhook to get the message from.
        webhook_token : str
            The token of the webhook to get the message from.
        message_id : int
            The ID of the message to get.
        thread_id : id, optional
            The ID of the thread to get the message from, by default None

        Returns
        -------
        ClientResponse
            A message object.
        """
        path = f'/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}'
        bucket = 'GET' + path
        return self._request('GET', path, bucket, auth=False)

    async def edit_webhook_message(self, webhook_id: int, webhook_token: str, message_id: int, thread_id: int = None, content: str = None, embeds: List[dict] = None, allowed_mentions: Any = None, components: List[Any] = None) -> ClientResponse:
        """Edit a message from a webhook.

        Parameters
        ----------
        webhook_id : int
            The ID of the webhook to edit the message from.
        webhook_token : str
            The token of the webhook to edit the message from.
        message_id : int
            The ID of the message to edit.
        thread_id : int, optional
            ID of the thread the message is in, by default None
        content : str, optional
            The message contents (up to 2000 characters), by default None
        embeds : List[dict], optional
            Embedded rich content, by default None
        allowed_mentions : Any, optional
            Allowed mentions for the message, by default None
        components : List[Any], optional
            The components to include with the message, by default None

        Returns
        -------
        ClientResponse
            A message object.
        """
        path = f'/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}'
        bucket = 'PATCH' + path

        payload = {
            'content': content,
            'embeds': embeds,
            'allowed_mentions': allowed_mentions,
            'components': components
        }
        return self._request('PATCH', path, bucket, json=payload, auth=False)

    async def delete_webhook_message(self, webhook_id: int, webhook_token: str, message_id: int) -> ClientResponse:
        """Delete a message from a webhook.

        Parameters
        ----------
        webhook_id : int
            The ID of the webhook to delete the message from.
        webhook_token : str
            The token of the webhook to delete the message from.
        message_id : int
            The ID of the message to delete.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}'
        bucket = 'DELETE' + path
        return self._request('DELETE', path, bucket, auth=False)

    """
    Interactions
    """

    async def create_interaction_response(self, interaction_id: int, interaction_token: str, type: int, data: dict = None) -> ClientResponse:
        """Create an interaction response.

        Parameters
        ----------
        interaction_id : int
            The ID of the interaction to create the response for.
        interaction_token : str
            The token of the interaction to create the response for.
        type : int
            The type of response to create.
        data : Any, optional
            An optional response message, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/interactions/{interaction_id}/{interaction_token}/callback'
        bucket = 'POST' + path
        payload = {
            'type': type
        }
        if data is not None:
            payload['data'] = data
        return self._request('POST', path, bucket, json=payload)

    async def get_original_interaction_response(self, application_id: int, interaction_token: str) -> ClientResponse:
        """Get the original interaction response.

        Parameters
        ----------
        application_id : int
            The ID of the application to get the original interaction response for.
        interaction_token : str
            The token of the interaction to get the original interaction response for.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/webhooks/{application_id}/{interaction_token}/messages/@original'
        bucket = 'GET' + path
        return self._request('GET', path, bucket)

    async def edit_original_interaction_response(self, application_id: int, interaction_token: str, content: str = None, embeds: List[dict] = None, allowed_mentions: Any = None, components: List[Any] = None) -> ClientResponse:
        """Edit the original interaction response.

        Parameters
        ----------
        application_id : int
            The ID of the application to edit the original interaction response for.
        interaction_token : str
            The token of the interaction to edit the original interaction response for.
        content : str, optional
            The message contents (up to 2000 characters), by default None
        embeds : List[dict], optional
            Embedded rich content, by default None
        allowed_mentions : Any, optional
            Allowed mentions for the message, by default None
        components : List[Any], optional
            The components to include with the message, by default None

        Returns
        -------
        ClientResponse
            A message object.
        """
        path = f'/webhooks/{application_id}/{interaction_token}/messages/@original'
        bucket = 'PATCH' + path

        payload = {
            'content': content,
            'embeds': embeds,
            'allowed_mentions': allowed_mentions,
            'components': components
        }

        return self._request('PATCH', path, bucket, json=payload)

    async def delete_original_interaction_response(self, application_id: int, interaction_token: str) -> ClientResponse:
        """Delete the original interaction response.

        Parameters
        ----------
        application_id : int
            The ID of the application to delete the original interaction response for.
        interaction_token : str
            The token of the interaction to delete the original interaction response for.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/webhooks/{application_id}/{interaction_token}/messages/@original'
        bucket = 'DELETE' + path
        return self._request('DELETE', path, bucket)

    async def create_followup_message(self, application_id: int, interaction_token: str, content: str = None, tts: bool = None, embeds: List[dict] = None, allowed_mentions: Any = None, components: List[Any] = None) -> ClientResponse:
        """Create a followup message.

        Parameters
        ----------
        application_id : int
            The ID of the application to create the followup message for.
        interaction_token : str
            The token of the interaction to create the followup message for.
        content : str, optional
            The message contents (up to 2000 characters), by default None
        tts : bool, optional
            True if this is a TTS message, by default None
        embeds : List[dict], optional
            Embedded rich content, by default None
        allowed_mentions : Any, optional
            Allowed mentions for the message, by default None
        components : List[Any], optional
            The components to include with the message, by default None

        Returns
        -------
        ClientResponse
            A message object.
        """
        path = f'/webhooks/{application_id}/{interaction_token}'
        bucket = 'POST' + path

        payload = {}

        if content is not None:
            payload['content'] = content
        if tts is not None:
            payload['tts'] = tts
        if embeds is not None:
            payload['embeds'] = embeds
        if allowed_mentions is not None:
            payload['allowed_mentions'] = allowed_mentions
        if components is not None:
            payload['components'] = components

        return self._request('POST', path, bucket, json=payload)

    async def get_followup_message(self, application_id: int, interaction_token: str, message_id: int) -> ClientResponse:
        """Get a followup message.

        Parameters
        ----------
        application_id : int
            The ID of the application to get the followup message for.
        interaction_token : str
            The token of the interaction to get the followup message for.
        message_id : int
            The ID of the message to get.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = f'/webhooks/{application_id}/{interaction_token}/messages/{message_id}'
        bucket = 'GET' + path
        return self._request('GET', path, bucket)

    async def edit_followup_message(self, application_id: int, interaction_token: str, message_id: int, content: str = None, embeds: List[dict] = None, allowed_mentions: Any = None, components: List[Any] = None) -> ClientResponse:
        """Edit a followup message.

        Parameters
        ----------
        application_id : int
            The ID of the application to edit the followup message for.
        interaction_token : str
            The token of the interaction to edit the followup message for.
        message_id : int
            The ID of the message to edit.
        content : str, optional
            The message contents (up to 2000 characters), by default None
        embeds : List[dict], optional
            Embedded rich content, by default None
        allowed_mentions : Any, optional
            Allowed mentions for the message, by default None
        components : List[Any], optional
            The components to include with the message, by default None

        Returns
        -------
        ClientResponse
            A message object.
        """
        path = f'/webhooks/{application_id}/{interaction_token}/messages/{message_id}'
        bucket = 'PATCH' + path

        payload = {
            'content': content,
            'embeds': embeds,
            'allowed_mentions': allowed_mentions,
            'components': components
        }

        return self._request('PATCH', path, bucket, json=payload)

    async def delete_followup_message(self, application_id: int, interaction_token: str, message_id: int, thread_id : id = None) -> ClientResponse:
        """Delete a followup message.

        Parameters
        ----------
        application_id : int
            The ID of the application to delete the followup message for.
        interaction_token : str
            The token of the interaction to delete the followup message for.
        message_id : int
            The ID of the message to delete.
        thread_id : id, optional
            ID of the thread the message is in, by default None

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        payload = {}
        if thread_id is not None:
            payload['thread_id'] = thread_id
        path = f'/webhooks/{application_id}/{interaction_token}/messages/{message_id}'
        bucket = 'DELETE' + path
        return self._request('DELETE', path, bucket, payload=payload)

    """
    Misc
    """

    async def get_gateway(self) -> ClientResponse:
        """Get the gateway URL.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = '/gateway'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket, auth=False)

    async def get_bot_gateway(self) -> ClientResponse:
        """Get the gateway URL for a bot.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = '/gateway/bot'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def application_info(self) -> ClientResponse:
        """Get the application info.

        Returns
        -------
        ClientResponse
            An application object.
        """
        path = '/oauth2/applications/@me'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket)

    async def authorisation_info(self, bearer_token: str) -> ClientResponse:
        """Get the authorisation info.

        Parameters
        ----------
        bearer_token : str
            The bearer token to get the authorisation info for.

        Returns
        -------
        ClientResponse
            The response from Discord.
        """
        path = '/oauth2/@me'
        bucket = 'GET' + path
        return await self._client._request('GET', path, bucket, headers={'Authorization': f'Bearer {bearer_token}'}, auth=False) # auth is False as a bearer_token is used
