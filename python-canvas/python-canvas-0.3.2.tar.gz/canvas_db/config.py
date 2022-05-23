class Config:
    def __init__(self, host, user, password, name='canvas_production'):
        self.host = host
        self.user = user
        self.password = password.replace('@', '%40')
        self.name = name
