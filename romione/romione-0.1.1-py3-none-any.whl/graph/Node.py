from sympy import Symbol
from sympy.solvers import solve
from sympy.parsing.sympy_parser import parse_expr

from romione.graph.compute_utils import parse_vector

class Node(object):

	def __init__(
		self, 
		name="s",
		value=0,
		eqn=None,
		graph=None,
	):

		self.name = name if eqn else Symbol(name)
		self.value = parse_vector(value)
		self.graph = graph
		self.eqn = eqn
		
		if eqn is not None:
			eqn = [i.strip() for i in eqn.split("=")]
			self.lhs = parse_expr(eqn[0])
			self.rhs = parse_expr(eqn[1])

		self.add_edges()

	def add_edges(self):
		if self.graph is not None:
			symbols = self.get_symbols()
			for s in symbols:
				self.graph.add_edge(s.name, self.name)


	def get_symbols(self):
		symbols = set()
		if self.eqn is not None:
			stack = [self.lhs, self.rhs]
			while stack:
				op = stack.pop()

				# operator is a symbol e.g. lhs in v = u + a * t
				if isinstance(op, Symbol) and op not in symbols:
					symbols.add(op)

				else:
					for args in op.args:					
						if isinstance(args, Symbol) and args not in symbols:
							symbols.add(args)
						else:
							stack.append(args)
		
		return symbols

	def get_complexity(self):
		complexity = 0
		if self.eqn is not None:
			stack = [self.lhs, self.rhs]
			while stack:
				op = stack.pop()
				sub_complexity = 0

				# operator is a symbol e.g. lhs in v = u + a * t
				if isinstance(op, Symbol) and self.graph.nodes[op.name]["node"].value is None:
					sub_complexity = 1

				else:
					for args in op.args:
						pass

				complexity += sub_complexity


		return complexity

	def solve(self):
		if self.eqn is not None:
			solve_for = []
			eqn = self.lhs - self.rhs

			for i in self.graph.pred[self.name]:
				node = self.graph.nodes[i]["node"]
				if isinstance(node.name, Symbol):
					if node.value is None:
						solve_for.append(node.name)
					else:
						eqn = eqn.subs(node.name, node.value)
			
			res = solve(eqn, *solve_for)

			return res

	def propagate(self):
		raise NotImplementedError