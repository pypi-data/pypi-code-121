from user import User


class emojiClass:
    def __init__(self, data):
        self.id = data.get("id")
        self.name = data.get("name")
        self.roles = data.get("roles")
        self.user = User(data.get("user"))
        self.require_colons = data.get("require_colons")
        self.managed = data.get("managed")
        self.animated = data.get("animated")
        self.available = data.get("available")
