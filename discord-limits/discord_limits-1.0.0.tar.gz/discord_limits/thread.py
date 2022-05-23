#https://discord.com/developers/docs/topics/threads
class Thread:
    def __init__(self, data):
        self.id = data.get("id")
        self.guild_id = data.get("guild_id")
        self.parent_id = data.get("parent_id")
        self.owner_id = data.get("owner_id")
        self.type = data.get("type")
        self.name = data.get("name")
        self.last_message_id = data.get("last_message_id")
        self.thread_metadata = ThreadMetadata(data.get("thread_metadata"))
        self.message_count = data.get("message_count")
        self.member_count = data.get("member_count")
        self.rate_limit_per_user = data.get("rate_limit_per_user")
        self.flags = data.get("flags")


class ThreadMetadata:
    def __init__(self, data):
        self.archived = data.get("archived")
        self.archive_timestamp = data.get("archive_timestamp")
        self.auto_archive_duration = data.get("auto_archive_duration")
        self.locked = data.get("locked")
        self.create_timestamp = data.get("create_timestamp")
