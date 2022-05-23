import sys
from importlib import resources
import json
from boozetools.support import runtime, interfaces
from bedspread import syntax

class Parser(runtime.TypicalApplication):
	RESERVED = {
		'AND' : syntax.Logical,
		'OR' : syntax.Logical,
		'XOR' : syntax.Logical,
		'EQV' : syntax.Logical,
		'MOD' : syntax.Operator,
		'NOT' : syntax.Operator,
		'AS': syntax.Operator,
		'WHEN': syntax.Operator,
		'THEN': syntax.Operator,
		'ELSE': syntax.Operator,
	}
	__confusing_token : syntax.Syntax = None
	def __init__(self):
		super().__init__(json.loads(resources.read_binary("bedspread", "grammar.automaton")))
	
	def scan_ignore(self, yy: interfaces.Scanner, what_to_ignore): pass
	def scan_punctuation(self, yy: interfaces.Scanner): syntax.Operator(yy, sys.intern(yy.matched_text()))
	
	def scan_real(self, yy: interfaces.Scanner): syntax.Literal(yy, float)
	def scan_imaginary(self, yy: interfaces.Scanner): syntax.Literal(yy, lambda t :float(t[:-1])*1j)
	def scan_hexadecimal(self, yy: interfaces.Scanner): syntax.Literal(yy, lambda t :int(yy.matched_text(), 16))
	
	scan_relop = syntax.RelOp
	
	def scan_word(self, yy: interfaces.Scanner):
		upper = yy.matched_text().upper()
		if upper in self.RESERVED:
			self.RESERVED[upper](yy, sys.intern(upper))
		else:
			syntax.Name(yy)
			
	def scan_token(self, yy: interfaces.Scanner, kind):
		text = yy.matched_text()
		yy.token(kind, text)
	
	parse_binary_operation = syntax.BinEx
	parse_case = syntax.Case
	parse_switch = syntax.Switch
	parse_unary = syntax.Unary
	parse_error = syntax.Error
	parse_apply = syntax.Apply
	parse_bind = syntax.Binding
	parse_parenthetical = syntax.Parenthetical
	parse_block = syntax.Block
	
	def parse_abstraction(self, parameter, body):
		if isinstance(parameter, syntax.Error): return parameter
		elif isinstance(body, syntax.Error): return body
		else: return syntax.Abstraction(parameter, body)
	
	def parse_broken_apply(self, abstraction, argument):
		return syntax.Apply(abstraction, syntax.Error(argument))
	
	def parse_first_binding(self, binding:syntax.Binding):
		return {binding.name.text:binding}
	
	def parse_another_binding(self, some:dict[str:syntax.Binding], another:syntax.Binding):
		name = another.name.text
		if name in some:
			return syntax.Error(name, "already used earlier")
		else:
			some[name] = another
			return some
	
	def parse_first_case(self, item:syntax.Case):
		return [item]
	
	def parse_another_case(self, some:list[syntax.Case], another:syntax.Case):
		some.append(another)
		return some
	
	def parse_two_params(self, alpha:syntax.Name, bravo:syntax.Name):
		a, b = alpha.text, bravo.text
		if a == b: return syntax.Error(bravo, "already used earlier")
		else: return {a:alpha, b:bravo}
	
	def parse_another_param(self, some: dict[str: syntax.Name], another: syntax.Name):
		name = another.text
		if name in some:
			return syntax.Error(another, "already used earlier")
		else:
			some[name] = another
			return some
	
	def unexpected_token(self, symbol, semantic, pds):
		self.__confusing_token = semantic
	
	def unexpected_eof(self, pds):
		self.__confusing_token = syntax.Noise(self.yy.current_span())
		
	def unexpected_character(self, yy: interfaces.Scanner):
		yy.token("NOISE", syntax.Noise(yy.current_span()))
		
	def will_recover(self, proposal):
		""" return an error token corresponding to the  """
		left = self.__confusing_token
		right = proposal[0][1] or syntax.Noise(self.yy.current_span())
		return syntax.Noise(syntax.interval(left, right))