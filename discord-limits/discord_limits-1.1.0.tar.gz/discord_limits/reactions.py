from member import MemberUser
from emoji import Emoji


"""
{'user_id': '443332743276003329', 'message_id': '864074491973599264', 'member': {'user': {'username': 'ninjafella', 'public_flags': 256, 'id': '443332743276003329', 'discriminator': '8777', 'avatar': '5d82466d79816197e192bcb94efd554f'}, 'roles': ['668872691549470735'], 'premium_since': None, 'pending': False, 'nick': None, 'mute': False, 'joined_at': '2020-01-20T17:40:57.787000+00:00', 'is_pending': False, 'hoisted_role': '668872691549470735', 'deaf': False}, 'emoji': {'name': '🤣', 'id': None}, 'channel_id': '668872612134256647', 'guild_id': '668872612134256641'}
"""


class ReactionAdd:
    def __init__(self, data):
        self.user_id = data.get("user_id")
        self.message_id = data.get("message_id")
        self.member = MemberUser(data.get("member"))
        self.emoji = Emoji(data.get("emoji"))
        self.channel_id = data.get("channel_id")
        self.guild_id = data.get("guild_id")


"""
{'user_id': '443332743276003329', 'message_id': '864074491973599264', 'emoji': {'name': '🤣', 'id': None}, 'channel_id': '668872612134256647', 'guild_id': '668872612134256641'}
"""


class ReactionRemove:
    def __init__(self, data):
        self.user_id = data.get("user_id")
        self.message_id = data.get("message_id")
        self.emoji = Emoji(data.get("emoji"))
        self.channel_id = data.get("channel_id")
        self.guild_id = data.get("guild_id")
