import numpy as np


def add(a: "Variable", b: "Variable"):
    """
    y = a + b
    """
    if type(b) != Variable:
        b = Variable(b)
    return Variable(a.value + b.value, "add", (a, b), a.require_grad or b.require_grad)


def sub(a: "Variable", b: "Variable"):
    """
    y = a - b
    """
    if type(a) != Variable:
        a = Variable(a)
    if type(b) != Variable:
        b = Variable(b)
    return Variable(a.value - b.value, "sub", (a, b), a.require_grad or b.require_grad)


def mul(a: "Variable", b: "Variable"):
    """
    y = a * b
    """
    if type(b) != Variable:
        b = Variable(b)
    return Variable(a.value * b.value, "mul", (a, b), a.require_grad or b.require_grad)


def matmul(a: "Variable", b: "Variable"):
    """
    y = a @ b
    """
    if type(b) != Variable:
        b = Variable(b)
    return Variable(a.value @ b.value, "matmul", (a, b), a.require_grad or b.require_grad)


def truediv(a: "Variable", b: "Variable"):
    """
    y = a / b
    """
    if type(a) != Variable:
        a = Variable(a)
    if type(b) != Variable:
        b = Variable(b)
    return Variable(a.value / b.value, "div", (a, b), a.require_grad or b.require_grad)


def pow(a: "Variable", b: "Variable"):
    """
    y = a ** b
    """
    if b == 0:
        return Variable(1)
    elif a == 0:
        return Variable(0)
    else:
        if type(a) != Variable:
            a = Variable(a)
        if type(b) != Variable:
            b = Variable(b)
        return Variable(a.value ** b.value, "pow", (a, b), a.require_grad or b.require_grad)


def log(x: "Variable"):
    """
    y = ln(x)
    """
    if type(x) != Variable:
        x = Variable(x)
    return Variable(np.log(x.value), "ln", (x,), x.require_grad)


def exp(x: "Variable"):
    """
    y = exp(x)
    """
    if type(x) != Variable:
        x = Variable(x)
    return Variable(np.exp(x.value), "exp", (x,), x.require_grad)


def diff(node, func):
    if func == "add":
        one = Variable(np.ones_like(node[0].value))
        return one, one
    elif func == "mul":
        return node[::-1]
    elif func == "matmul":
        return node[1].T, node[0].T
    elif func == "pow":
        return node[1] * (node[0] ** (node[1] - 1)), node[0] ** node[1] * log(node[0])
    elif func == "div":
        return 1 / node[1], -node[0] / node[1] ** 2
    elif func == "sub":
        one = Variable(np.ones_like(node[0].value))
        neg_one = Variable(-np.ones_like(node[0].value))
        return one, neg_one
    elif func == "exp":
        return exp(node[0]),
    elif func == "log":
        return 1 / node[0],


class Variable:
    def __init__(self, value=None, grad_fn=None, node=None, require_grad=False):
        if type(value) is not np.array:
            value = np.array(value)
        self.value = value
        self.grad_fn = grad_fn
        self.node = node
        self.grad = None
        self.require_grad = require_grad
        self.shape = self.value.shape

    def __str__(self):
        return "Variable({})".format(np.round(self.value, 2))

    def __add__(self, other):
        return add(self, other)

    def __iadd__(self, other):
        return add(self, other)

    def __radd__(self, other):
        return add(self, other)

    def __sub__(self, other):
        return sub(self, other)

    def __isub__(self, other):
        return sub(self, other)

    def __rsub__(self, other):
        return sub(other, self)

    def __neg__(self):
        return sub(Variable(np.zeros_like(self.value)), self)

    def __mul__(self, other):
        return mul(self, other)

    def __matmul__(self, other):
        return matmul(self, other)

    def __imul__(self, other):
        return mul(self, other)

    def __rmul__(self, other):
        return mul(self, other)

    def __truediv__(self, other):
        return truediv(self, other)

    def __idiv__(self, other):
        return truediv(self, other)

    def __rtruediv__(self, other):
        return truediv(other, self)

    def __pow__(self, power):
        return pow(self, power)

    def __rpow__(self, other):
        return pow(other, self)

    @property
    def T(self):
        return Variable(self.value.T, "transpose", (self, ), self.require_grad)

    def detach(self):
        return Variable(self.value, require_grad=self.require_grad)

    def backward(self, grad=None):
        if grad is not None:
            if type(grad) != Variable:
                grad = Variable(grad)
            if self.grad:
                self.grad += grad
            else:
                self.grad = grad

        if self.grad_fn == "transpose":
            node = self.node[0]
            if node.require_grad and grad is not None:
                node.backward(grad.T)
            else:
                node.backward(np.eye(node.shape[0]))
        elif self.grad_fn is not None:
            grad_ = diff(self.node, self.grad_fn)
            if grad:
                for i, node in enumerate(self.node):
                    if node.require_grad:
                        if self.grad_fn == "matmul":
                            if i == 0:
                                node.backward(grad @ grad_[i])
                            else:
                                node.backward(grad_[i] @ grad)
                        else:
                            node.backward(grad * grad_[i])
            else:
                for i, node in enumerate(self.node):
                    if node.require_grad:
                        node.backward(grad_[i])

    def zero_grad(self):
        self.grad = None
        if self.node:
            for node in self.node:
                node.zero_grad()
