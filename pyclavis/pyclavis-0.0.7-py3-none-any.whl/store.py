class CredentialStore(object):
    def __init__(self):
        self.store = {}

    def __repr__(self):
        return self.__class__.__name__ + " " + str(self.store)

    def clear(self):
        self.store.clear()

    def _get_cat_def(self, cred):
        return self.store.setdefault(str(cred.category).lower(), {})

    def set(self, cred):
        cat = self._get_cat_def(cred)
        cat[cred.name.lower()] = cred

    def remove(self, cred):
        try:
            cat = self._get_cat_def(cred)
            del cat[cred.name.lower()]
            if len(cat) == 0:
                del self.store[str(cred.category).lower()]
        except Exception as ex:
            print(ex)

    def get(self, name, category=None):
        try:
            cat = self.store[str(category).lower()]
            return cat[name.lower()]
        except:
            return None

    def tolist(self):
        elem = []
        for v in self.store.values():
            elem.extend(v.values())
        return elem

    def fromlist(self, elem, clear=True):
        if clear:
            self.clear()
        for c in elem:
            self.set(c)
