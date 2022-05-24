from itertools import cycle


class RotateAccounts:
    def __init__(self, accounts):
        self.cycleAccount = cycle(accounts)

    def nextAccount(self):
        return next(self.cycleAccount)
