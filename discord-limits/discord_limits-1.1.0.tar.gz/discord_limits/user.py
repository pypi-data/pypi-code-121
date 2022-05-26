class User:
    def __init__(self, data):
        self.username = data.get('username')
        self.public_flags = data.get('public_flags')
        self.id = data.get('id')
        self.discriminator = data.get('discriminator')
        self.avatar = data.get('avatar')
        self.pfp = self.__get_avatar()
        self.bot = data.get('bot')
        self.system = data.get('system')
        self.mfa_enabled = data.get('mfa_enabled')
        self.locale = data.get('locale')
        self.verified = data.get('verified')
        self.email = data.get('email')
        self.flags = data.get('flags')
        self.premium_type = data.get('premium_type')

    def __get_avatar(self): #Changing the icon code of the user to the url that we then use on the webpage
        icon = self.avatar
        if icon is not None: #If the icon id thingy exists create the link to it otherwise use the default discord icon
            return f"https://cdn.discordapp.com/avatars/{self.id}/{icon}.png"
        else:
            number = int(self.discriminator) % 5
            return f"https://cdn.discordapp.com/embed/avatars/{number}.png"
