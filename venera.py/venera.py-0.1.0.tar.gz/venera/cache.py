from typing import Dict


class Cache:
    def __init__(self):
        # ordered like:
        # guild_id: data
        self.guilds = {}
        # ordered like:
        # guild_id: [members ordered alphabetically]
        self.members = {}
        # ordered like:
        # guild_id: [channels]
        self.channels = {}
        # ordered like:
        # channel_id: {message_id: data}
        self.messages: Dict[int, Dict] = {}
        # ordered like:
        # user_id: data
        self.presences = {}
