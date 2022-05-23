"""
For the moment, just a read-parse-print loop.

"""
from bedspread import __version__, front_end, evaluator

def promptedInput():
	# Prompt for some input:
	return input("Ready >> ")


def usage():
	print("Bed Spread (version %s), interactive REPL"% __version__)
	print("    Documentation is at http://bedspread.readthedocs.io")
	print("    Follow progress at https://github.com/kjosib/bedspread")
	print("    This is pre-alpha code. Current goal is to pretty-print ASTs corresponding to expressions.")
	print("    ctrl-d or ctrl-z to quit, depending on your operating system")

def consoleLoop():
	# Read/Parse/Print Loop
	parser = front_end.Parser()
	while True:
		try: text = promptedInput()
		except EOFError: break
		if text:
			tree = parser.parse(text)
			value = evaluator.evaluate(tree)
			if isinstance(value, evaluator.Error):
				parser.source.complain(*value.exp.span())
			print(value)
		else: usage()
	

if __name__ == '__main__':
	usage()
	consoleLoop()
