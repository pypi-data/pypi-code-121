class Credential(object):
    def __init__(self, name=None, user=None, passwd=None, category=None):
        self.name = name
        self.user = user
        self.passwd = passwd
        self.category = (
            category if category != None and len(category.strip()) > 0 else None
        )

    def __repr__(self):
        return (
            self.__class__.__name__
            + "("
            + ", ".join([self.name, self.user, str(self.category)])
            + ")"
        )

    def todict(self):
        return {
            "CNAME": self.name,
            "USER": self.user,
            "PASSWORD": self.passwd,
        }
