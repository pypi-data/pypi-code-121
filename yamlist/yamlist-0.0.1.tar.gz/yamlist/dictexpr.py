import json

from yamlist import calculator
from yamlist import expr
from yamlist import strexpr
from yamlist import userfunc

class EvaluatingDict(expr.EvaluatingExpr):
    def __init__(self, expr, bindings):
        super().__init__(expr, bindings)
        self.prepared = None

    def fetch(self):
        prepared = self.prepare()
        if not isinstance(prepared, dict):
            return calculator.evaluate_final(prepared)
        dst = {}
        for key, elem in prepared.items():
            r = calculator.evaluate_final(elem)
            if not isinstance(r, calculator.NoElementValue):
                dst[key] = calculator.value_to_single(r)
        return dst

    def prepare(self):
        if self.prepared is not None:
            return self.prepared
        self.bindings2 = self.bindings.copy()
        for key, expr in self.get_consts().items():
            self.bindings2[key] = expr
        params = self.get_params()
        if len(params) == 0:
            self.prepared = self.prepare_dict()
        else:
            self.prepared = self.prepare_func(params)
        return self.prepared

    def prepare_dict(self):
        if "$_" in self.expr:
            return calculator.evaluate_final(calculator.buildEvaluating(self.expr["$_"], self.bindings2))
        body = {}
        for key, elem in self.expr.items():
            if key.startswith("$$"):
                key = key[1:]
            elif key.startswith("$"):
                key = None
            elif key.startswith("=$"):
                key_name_value = calculator.evaluate_final(calculator.buildEvaluating(key[1:], self.bindings2))
                key = strexpr.value_to_string(key_name_value)
            if key is not None:
                body[key] = calculator.buildEvaluating(elem, self.bindings2)
        return body

    def prepare_func(self, params):
        body = self.prepare_func_body()
        return userfunc.UserFunction(body, params, self.bindings)

    def prepare_func_body(self):
        if "$_" in self.expr:
            return self.expr["$_"]
        body = {}
        for key, elem in self.expr.items():
            if key.startswith("$") and not key.startswith("$$") and key != "$_":
                if elem == "$param":
                    continue
            body[key] = elem
        return body

    def get_consts(self):
        consts = {}
        for key, elem in self.expr.items():
            if key.startswith("$") and not key.startswith("$$") and key != "$_":
                if elem != "$param":
                    consts[key[1:]] = calculator.buildEvaluating(elem, self.bindings2)
        return consts

    def get_params(self):
        params = []
        for key, elem in self.expr.items():
            if key.startswith("$") and not key.startswith("$$") and key != "$_":
                if elem == "$param":
                    params.append(key[1:])
        return params

    def exists_name(self, name):
        prepared = self.prepare()
        if not isinstance(prepared, dict):
            return False
        n1, n2 = parse_name(name)
        if n1 in prepared:
            return calculator.exists_in_bindings(prepared[n1], n2)
        else:
            return False

    def get_by_name(self, name):
        prepared = self.prepare()
        if not isinstance(prepared, dict):
            return None
        n1, n2 = parse_name(name)
        if n1 in prepared:
            return calculator.get_from_bindings(prepared[n1], n2)
        else:
            return None

