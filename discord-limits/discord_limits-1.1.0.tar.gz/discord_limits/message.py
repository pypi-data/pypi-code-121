from member import Member
from user import User


class Message:
    def __init__(self, data):
        self.type = data.get("type")
        self.tts = data.get("tts")
        self.timestamp = data.get("timestamp")
        self.referenced_message = data.get("referenced_message")
        self.pinned = data.get("pinned")
        self.mentions = data.get("mentions")
        self.mention_roles = data.get("mention_roles")
        self.mention_everyone = data.get("mention_everyone")
        self.nonce = data.get("nonce") #Used for validating a message was sent
        try:
            self.member = Member(data.get("member"))
        except Exception:
            self.member = None
        self.id = data.get("id")
        self.flags = data.get("flags") #https://discord.com/developers/docs/resources/channel#message-object-message-flags
        self.embeds = data.get("embeds")
        self.edited_timestamp = data.get("edited_timestamp")
        self.content = data.get("content")
        self.compenents = data.get("components")
        self.channel_id = data.get("channel_id")
        try:
            self.author = User(data.get("author"))
        except Exception:
            self.author = None
        self.attachments = data.get("attachments")
        self.guild_id = data.get("guild_id")
        self.thread = data.get("thread")
