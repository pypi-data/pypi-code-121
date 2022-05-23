import inspect
import operator
from . import syntax
import math

GLOBAL_SCOPE = {} ## Filled in at the end of the file with (most of) the math module.

PRIMITIVE_BINARY = {
	"^": operator.pow,
	"+": operator.add,
	"-": operator.sub,
	"*": operator.mul,
	"/": operator.truediv,
	"MOD": operator.mod,
	"EQ": operator.eq,
	"NE": operator.ne,
	"LT": operator.lt,
	"LE": operator.le,
	"GE": operator.ge,
	"GT": operator.gt,
	"OR": operator.or_,
	"AND": operator.and_,
	'XOR': operator.xor,
	'EQV': operator.is_,  # Hack, but works in context: True and False are singletons in Python's runtime.
}

PRIMITIVE_UNARY = {
	"-": operator.neg,
	"NOT": operator.not_,
}

class Error:
	""" A kind of value which means there is some error. """
	def __init__(self, exp:syntax.Syntax, problem:str):
		self.exp = exp
		self.problem = problem
	def __str__(self):
		return "<<Error: %s %s>>"%(self.exp.span(), self.problem)

class Function:
	""" A kind of value that can be applied to create new values """
	def has_parameter(self, name:str) -> bool:
		raise NotImplementedError(type(self))

	def eval(self, arg, caller_env):
		""" arg is caller syntax and env is the caller's scope. """
		raise NotImplementedError(type(self))

class MultaryFunction(Function):
	def __init__(self, parameter_names):
		self.parameter_names = set(parameter_names)
	
	def has_parameter(self, name: str) -> bool:
		return name in self.parameter_names
	
	def __bad_call(self, arg):
		return Error(arg, "Multi-parameter function expects named arguments %r" % self.parameter_names)

	def eval(self, arg, caller_env):
		if isinstance(arg, dict):
			extra = arg.keys() - self.parameter_names
			if extra: return self.__bad_call(arg[extra.pop()])
			free = self.parameter_names - arg.keys()
			bound = {}
			for k, v in arg.items():
				value = _eval(v.argument, caller_env)
				if isinstance(value, Error): return value
				bound[k] = value
			if free: return PartialFunction(self, bound, free)
			return self.raw_multi(bound)
		else:
			return self.__bad_call(arg)

	def raw_multi(self, bound:dict[str:object]):
		raise NotImplementedError(type(self))

class PartialFunction(MultaryFunction):
	def __init__(self, basis:MultaryFunction, bound:dict, free:set):
		self.basis = basis
		self.bound = bound
		super().__init__(free)
	
	def raw_multi(self, bound:dict[str:object]):
		return self.basis.raw_multi({**self.bound, **bound})

class UnaryFunction(Function):
	def has_parameter(self, name: str) -> bool:
		return False

	def eval(self, arg, caller_env):
		if isinstance(arg, dict):
			first_arg = next(iter(arg.values()))
			return Error(first_arg, "Unary Function expects a single unadorned argument.")
		else:
			value = _eval(arg, caller_env)
			if isinstance(value, Error): return value
			return self.raw_single(value)

	def raw_single(self, value:object):
		raise NotImplementedError(type(self))


class PythonUnary(UnaryFunction):
	def __init__(self, fn):
		self.raw_single = fn
	
class PythonMultary(MultaryFunction):
	def __init__(self, fn, params):
		super().__init__(params)
		self.__fn = fn
		self.param_order = tuple(params)
	
	def raw_multi(self, bound:dict[str:object]):
		return self.__fn(*(bound[k] for k in self.param_order))
	

class UDF1(UnaryFunction):
	def __init__(self, tree:syntax.Abstraction, env):
		self.parameter = tree.parameter.text
		self.body = tree.body
		self.lexical_scope = env
		
	def raw_single(self, value:object):
		activation_env = {**self.lexical_scope, self.parameter: value}
		return _eval(self.body, activation_env)
	
class UDF2(MultaryFunction):
	def __init__(self, tree: syntax.Abstraction, env):
		super().__init__(tree.parameter.keys())
		self.body = tree.body
		self.lexical_scope = env
	
	def raw_multi(self, bound: dict[str:object]):
		activation_env = {**self.lexical_scope, **bound}
		return _eval(self.body, activation_env)
	
def evaluate(tree):
	return _eval(tree, GLOBAL_SCOPE)

def _select_primitive(op:syntax.Operator):
	if isinstance(op, syntax.RelOp): return op.relation
	elif isinstance(op, syntax.Logical): return op.logic
	else: return op.kind

def _eval(tree, env):
	# Converts SYNTAX to VALUE
	if isinstance(tree, syntax.Literal):
		return tree.value
	elif isinstance(tree, syntax.Name):
		try: return env[tree.text]
		except KeyError: return Error(tree, "No such name in scope.")
	elif isinstance(tree, syntax.BinEx):
		lhs = _eval(tree.lhs, env)
		if isinstance(lhs, Error):
			return lhs
		else:
			rhs = _eval(tree.rhs, env)
			if isinstance(rhs, Error):
				return rhs
			else:
				primitive = PRIMITIVE_BINARY[_select_primitive(tree.op)]
				try: return primitive(lhs, rhs)
				except Exception as e: return Error(tree, repr(e))
	elif isinstance(tree, syntax.Unary):
		operand = _eval(tree.exp, env)
		if isinstance(operand, Error):
			return operand
		else:
			return PRIMITIVE_UNARY[tree.op.kind](operand)
	elif isinstance(tree, syntax.Parenthetical):
		return _eval(tree.exp, env)
	elif isinstance(tree, syntax.Block):
		return _eval(tree.exp, env)
	elif isinstance(tree, syntax.Apply):
		function = _eval(tree.function, env)
		if isinstance(function, Error): return function
		elif isinstance(function, Function):
			try: return function.eval(tree.argument, env)
			except Exception as e: return Error(tree, repr(e))
		else: return Error(tree.function, "is not a function.")
	elif isinstance(tree, syntax.Abstraction):
		if isinstance(tree.parameter, syntax.Name):
			return UDF1(tree, env)
		elif isinstance(tree.parameter, dict):
			return UDF2(tree, env)
		else:
			raise RuntimeError("This can't happen.")
	elif isinstance(tree, syntax.Switch):
		for case in tree.cases:
			test = _eval(case.predicate, env)
			if test is True: return _eval(case.consequence, env)
			elif test is not False: return Error(case.predicate, "did not evaluate as a Boolean predicate")
		else:
			return _eval(tree.otherwise, env)
	elif isinstance(tree, syntax.Error):
		return Error(tree, "Syntax Error")
	raise RuntimeError("Incomplete Evaluator: ", tree)

### Here's the part that pre-loads some global functions to play with:

for name in dir(math):
	if name.startswith('_'): continue
	it = getattr(math, name)
	if callable(it):
		try: signature = inspect.signature(it)
		except ValueError: continue
		if len(signature.parameters) == 1:
			GLOBAL_SCOPE[name] = PythonUnary(it)
		elif all(len(k)==1 for k in signature.parameters.keys()):
			GLOBAL_SCOPE[name] = PythonMultary(it, signature.parameters.keys())
	else:
		GLOBAL_SCOPE[name] = it

