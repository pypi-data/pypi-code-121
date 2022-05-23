"""
Syntax Tree Components
This is probably going to end up object-oriented for now.
Bollox.


Observation:
The vast bulk of what's here is boilerplate.
A first-round context-free analysis produces a straightforward data structure in a bottom-up manner.
What you can then do with that data structure depends on how easy subsequent passes are to write.

"""
from typing import Union

class Syntax:
	def span(self) -> tuple[int, int]:
		raise NotImplementedError(type(self))

def interval(a,b) -> tuple[int, int]:
	""" For composing spans. """
	# This is affected by the odd span format.
	left = a.span()[0]
	right = sum(b.span())
	return left, (right - left)

class Noise(Syntax):
	def __init__(self, span):
		self._span = span
	
	def span(self):
		return self._span
	
	def __str__(self):
		return "<<%s,%s>>"%self._span


class Operator(Syntax):
	_span : tuple[int, int]
	
	def __init__(self, yy, kind):
		self._span = yy.current_span()
		self.kind = kind
		yy.token(kind, self)
	
	def span(self):
		return self._span
	
	def excerpt(self, text):
		left, count = self._span
		return text[left:left + count]
	
	def __str__(self):
		return self.kind

class Atom(Operator):
	def __init__(self, yy, kind):
		super().__init__(yy, kind)
		self.text = yy.matched_text()
	def __str__(self):
		return self.text

class Name(Atom):
	def __init__(self, yy):
		super().__init__(yy, "NAME")

class Literal(Atom):
	def __init__(self, yy, read):
		super().__init__(yy, "LITERAL")
		self.value = read(self.text)
	pass

class RelOp(Operator):
	CANONICAL = {
		'EQ':'==',
		'NE':'!=',
		'LT':'<',
		'LE':'<=',
		'GT':'>',
		'GE':'>=',
	}
	def __init__(self, yy, relation):
		super().__init__(yy, "RELOP")
		self.text = self.CANONICAL[relation]
		self.relation = relation
	def __str__(self):
		return self.CANONICAL[self.relation]

class Logical(Operator):
	def __init__(self, yy, logic):
		super().__init__(yy, "LOGIC")
		self.logic = logic
	def __str__(self):
		return self.logic

class Expression(Syntax):
	pass

class Error(Expression):
	def __init__(self, *args):
		self.args = args
		
	def span(self) -> tuple[int, int]:
		return interval(self.args[0], self.args[-1])
	
	def __str__(self):
		return "<<ERROR {%s}>>"%(str(self.args[0]))

class Unary(Expression):
	def __init__(self, op:Operator, exp:Expression):
		self.op = op
		self.exp = exp
	def span(self) -> tuple[int, int]:
		return interval(self.op, self.exp)

	def __str__(self):
		return "%s %s" % (self.op, self.exp)

class BinEx(Expression):
	def __init__(self, lhs:Expression, op:Operator, rhs:Expression):
		self.lhs = lhs
		self.op = op
		self.rhs = rhs
	
	def span(self) -> tuple[int, int]:
		return interval(self.lhs, self.rhs)
	
	def __str__(self):
		return "%s %s %s"%(self.lhs, self.op, self.rhs)

class Case(Expression):
	def __init__(self, predicate, consequence):
		self.predicate = predicate
		self.consequence = consequence
		
	def __str__(self):
		return "WHEN %s THEN %s; "%(self.predicate, self.consequence)
	
	def span(self) -> tuple[int, int]:
		return interval(self.predicate, self.consequence)
		
class Switch(Expression):
	def __init__(self, cases:list[Case], otherwise:Expression):
		self.cases = cases
		self.otherwise = otherwise
		
	def __str__(self):
		cases = ''.join(map(str, self.cases))
		return "{%sELSE %s}"%(cases, self.otherwise)

class Apply(Expression):
	def __init__(self, function:Expression, argument:Expression):
		self.function = function
		self.argument = argument
		
	def __str__(self):
		if isinstance(self.argument, dict):
			arg = ', '.join(map(str, self.argument.values()))
		else:
			arg = str(self.argument)
		return str(self.function)+"( " + arg + " )"
	
	def span(self) -> tuple[int, int]:
		return interval(self.function, self.argument)

class Abstraction(Expression):
	# Just a _syntax_ node.
	def __init__(self, parameter:Union[Name, dict[str,Name]], body:Expression):
		self.parameter = parameter
		self.body = body
		
	def __str__(self):
		if isinstance(self.parameter, dict): param_string = ', '.join(map(str, self.parameter.keys()))
		else: param_string = str(self.parameter)
		return "\\"+param_string+" "+str(self.body)

class Binding(Syntax):
	def __init__(self, name: Name, argument: Expression):
		self.name = name
		self.argument = argument
	def __str__(self):
		return str(self.name)+": "+str(self.argument)

class Parenthetical(Expression):
	def __init__(self, exp:Expression):
		self.exp = exp
	
	def __str__(self):
		return "("+str(self.exp)+")"
	
	def span(self) -> tuple[int, int]:
		return self.exp.span()

class Block(Expression):
	def __init__(self, exp:Expression):
		self.exp = exp
	
	def __str__(self):
		return "[" + str(self.exp) + "]"

	def span(self) -> tuple[int, int]:
		return self.exp.span()

