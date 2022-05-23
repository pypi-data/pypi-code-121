from user import User


class Member:
    def __init__(self, data):
        self.roles = data.get('roles')
        self.user = data.get('user')
        self.premuim_since = data.get('premium_since')
        self.pending = data.get('pending')
        self.nick = data.get('nick')
        self.mute = data.get('mute')
        self.joined_at = data.get('joined_at')
        self.deaf = data.get('deaf')


class MemberUser:
    def __init__(self, data):
        self.roles = data.get('roles')
        self.user = User(data.get('user'))
        self.premuim_since = data.get('premium_since')
        self.pending = data.get('pending')
        self.nick = data.get('nick')
        self.mute = data.get('mute')
        self.joined_at = data.get('joined_at')
        self.deaf = data.get('deaf')
