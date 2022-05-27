# This file is placed in the Public Domain.


"users"


from .obj import Class, Object, find, save, update


def __dir__():
    return (
        "NoUser",
        "Users",
    )


class NoUser(Exception):

    pass



class User(Object):

    def __init__(self, val=None):
        super().__init__()
        self.user = ""
        self.perms = []
        if val:
            update(self, val)


Class.add(User)


class Users(Object):

    userhosts = Object()

    def allowed(self, origin, perm):
        perm = perm.upper()
        origin = getattr(self.userhosts, origin, origin)
        user = self.get_user(origin)
        if user:
            if perm in user.perms:
                return True
        return False

    def delete(self, origin, perm):
        for user in self.get_users(origin):
            try:
                user.perms.remove(perm)
                save(user)
                return True
            except ValueError:
                pass

    def get_users(self, origin=""):
        s = {"user": origin}
        return find("user", s)

    def get_user(self, origin):
        u = list(self.get_users(origin))
        if u:
            return u[-1][-1]

    def perm(self, origin, permission):
        user = self.get_user(origin)
        if not user:
            raise NoUser(origin)
        if permission.upper() not in user.perms:
            user.perms.append(permission.upper())
            save(user)
        return user


Class.add(Users)
