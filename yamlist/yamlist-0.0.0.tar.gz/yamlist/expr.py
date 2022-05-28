from yamlist import calculator

class EvaluatingExpr:
    def __init__(self, expr, bindings):
        self.expr = expr
        self.bindings = bindings
        self.evaluated = None
        self.evaluated_flag = False

    def evaluate(self):
        if not self.evaluated_flag:
            self.evaluated = self.fetch()
            self.evaluated_flag = True
        return self.evaluated

    def fetch(self):
        raise Exception()

    def exists_name(self, name):
        value = self.evaluate()
        return calculator.exists_in_bindings(value)

    def get_by_name(self, name):
        value = self.evaluate()
        return calculator.get_from_bindings(value)

