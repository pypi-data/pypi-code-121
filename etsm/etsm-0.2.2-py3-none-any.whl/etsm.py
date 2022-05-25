class State:
    def __init__(self, enter, exit):
        self.Enter = enter
        self.Exit = exit

class StateMachine:
    def __init__(self, owner):
        self.Owner = owner
        self.Current = None

    def Transition(self, state) :
        if (self.Current != None and self.Current.Exit != None):
            self.Current.Exit(self.Owner)
        self.Current = state
        if (self.Current != None and self.Current.Enter != None):
            self.Current.Enter(self.Owner)

    def IsIn(self, state):
        return self.Current == state