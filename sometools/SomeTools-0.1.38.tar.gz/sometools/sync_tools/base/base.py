class Base:
    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)

    def help(self):
        raise NotImplementedError("尚未添加一个help方法")