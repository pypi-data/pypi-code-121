import sys
import templ8.blessing
import os
from templ8.divine import divine
from templ8.radio import radio
from templ8.genesis import genesis
from templ8.blessing import makedir
from templ8.pandoc import pandoc
from templ8.neo import neo
from templ8.help_args import help_cmd
import pkgutil

DEITY_PATH = "d8y"
DEF_BASEHTML_PATH = "basehtml"
DEF_REPLACE_PATH = "repl8ce"

DEF_INPUT = "input"
DEF_OUTPUT = "output"


def help(cmd=""):
	if cmd == "":
		print(templ8.blessing.TEMPL8_ASCII + "\n\n")
		print("Arguments in (parentheses) are optional. The ones in [brackets] are mandatory.\n")
		print("  help (command)   Display this list. If a command is given, displays instructions for that command.")
		print("  genesis [name]   Create a new templ8 project in a folder named [name].")
		print("  divine           Assemble a templ8 site.")
		print("  radio            Assemble a templ8 blog.")
		print("  neo              Upload all output files to Neocities.")
		print("  pandoc           Downloads a pandoc binary for markdown use.")
		print("")
	else:
		path = os.path.join("help", cmd)
		print("\n")
		print("=      == = ==  =  = ============ == = =   =         =")
		print("\n")
		print(help_cmd[cmd])
		print("\n")
		print("==     == ==== =  = ===== ======== == = =   ===      =")
		print("\n")

		


def main():
	if len(sys.argv) <= 1:
		help()
	elif sys.argv[1] == "help":
		if len(sys.argv) == 3:
			help(sys.argv[2])
		else:
			help()
	elif sys.argv[1] == "divine":
		divine()
	elif sys.argv[1] == "radio":
		radio()
	elif sys.argv[1] == "pandoc":
		pandoc()
	elif sys.argv[1] == "neo":
		neo()
	elif sys.argv[1] == "genesis":
		if len(sys.argv) >= 3:
			genesis(sys.argv[2])
		else:
			raise Exception("Unexpected number of arguments")
	else:
		raise Exception("Unknown command")
	
