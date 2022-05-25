class PermSet:
    def __init__(self, rn: str, action: str):
        self.rn, self.action = self.__normalize(rn, {action})
        self.action = self.action.pop()

    def __normalize(self, rn: str, actions: set):
        assert type(rn) is str
        assert type(actions) in [set, list]

        rn = [p.strip().lower() for p in rn.split(":")]
        actions = {a.strip().lower() for a in actions}

        return rn, actions

    def __cmp_actions(self, actions):
        return "*" in actions or self.action in actions

    def __cmp_rn(self, rn):
        # e.g. rn:a:b >>= rn:a:b
        if self.rn == rn:
            return True

        # e.g. rn:a:b:* >>= rn:a:b
        if self.rn + ["*"] == rn:
            return True

        # e.g. rn:a:* >>= rn:a:b:c
        return rn[-1] == "*" and rn[:-1] == self.rn[:len(rn)-1]

    @property
    def scope(self) -> str:
        if not getattr(self, "_scope", None):
            self._scope = ":".join(self.rn + [self.action])

        return self._scope

    def check(self, rn: str, actions: set) -> bool:
        rn, actions = self.__normalize(rn, actions)

        return self.__cmp_actions(actions) and self.__cmp_rn(rn)
