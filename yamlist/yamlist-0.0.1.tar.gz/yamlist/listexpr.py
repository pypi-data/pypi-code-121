import json

from yamlist import calculator
from yamlist import expr

class EvaluatingList(expr.EvaluatingExpr):
    def __init__(self, expr, bindings):
        super().__init__(expr, bindings)

    def fetch(self):
        src = self.expr
        src2 = []
        for elem in src:
            src2.append(calculator.evaluate_final(calculator.buildEvaluating(elem, self.bindings)))
        dst = self._flatten(src2)
        return dst

    def _flatten(self, items):
        result = []
        stack_if = []
        for elem in items:
            r = calculator.evaluate_final(elem)
            if isinstance(r, calculator.NoElementValue):
                pass
            elif isinstance(r, calculator.ListInListValue):
                if self._stack_all_true(stack_if):
                    result.extend(self._flatten(r.items))
            elif isinstance(elem, calculator.CondStackOperationValue):
                stack_if = r.operation(stack_if)
            else:
                if self._stack_all_true(stack_if):
                    result.append(calculator.value_to_single(elem))
        return result

    def _stack_all_true(self, stack_if):
        for elem in stack_if:
            if elem <= 0:
                return False
        return True

