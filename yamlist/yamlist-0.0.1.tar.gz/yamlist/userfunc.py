
from yamlist import calculator

class UserFunction:
    def __init__(self, body, arg_names, bindings):
        self.body = body
        self.arg_names = arg_names
        self.bindings = bindings

    def call_apply(self, args):
        bindings2 = self.bindings.copy()
        n = min(len(args), len(self.arg_names))
        for i in range(n):
            bindings2[self.arg_names[i]] = args[i]
        return calculator.buildEvaluating(self.body, bindings2)

