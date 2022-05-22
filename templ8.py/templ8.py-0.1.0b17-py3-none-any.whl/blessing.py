import os
import textile
import pypandoc

TEMPL8_ASCII = """
    ###                                                                 
    ###                                                               ###
    ###                                                               ###       #####
###########        ###                                                ###     ##    ###
###########     #########      ### ####    #####      ### ######      ###    ##      ###
    ###        ###     ###     ###################    ############    ###    ##     ####
    ###       ###       ###    ###    ####    ####    ###      ####   ###     ##   ####
    ###       #############    ###     ###     ###    ###       ###   ###      #######
    ###       #############    ###     ###     ###    ###      ####   ###    ####    ##
  #######     ###              ###     ###     ###    ############    ###   ####       ##
    ###       ####      ###    ###     ###     ###    ##########      ###   ###        ##
    ###         ##########     ###     ###     ###    ###             ###    ###     ###
    ##            ######       ###     ###     ###    ###             ###      ####### 
    ##                                                ###
    #"""
    
# Misnomer: This is the default blogbase
DEF_BASEHTML_CONTENT = """PAGETITLE=##TITLE##
-BEGINFILE-
h2. ##TITLE##

^##AUTHORS## - ##TAGS## - ##DATE##^

##CONTENT##

-BEGININDEX-
h2. "##TITLE##":##LINK##

^##AUTHORS## - ##TAGS## - ##DATE##^

##INTRO##
-BEGININDEX-
PAGETITLE=Blog"""

DEF_INPUT = "input"
DEF_OUTPUT = "output"
DEITY_PATH = "d8y"
DEF_BASEHTML_PATH = "basehtml"
DEF_REPLACE_PATH = "repl8ce"


# Checks if a directory exists and make it if not
def makedir(path, warning = ""):
	if not os.path.exists(path):
		if warning != "":
			print("WARNING: " + warning)
		os.mkdir(path)


# Processes the repl8ce of a header
def mod_replaces(input_replaces, header):
	# These variables are used for multiline keys
	current_multikey = "" # The current key being edited
	multiline = False
	
	for i in header.split("\n"):
		# Split it in the single line way
		keyval = i.split("=", 1)
		# If we're not processing multilines, and the current line is single line, set key
		if len(keyval) == 2 and not multiline:
			input_replaces[keyval[0]] = keyval[1].replace(r"\n", "\n")
		# If it's not a valid single line
		elif len(keyval) == 1 and keyval[0] != "":
			# If it's a valid multiline, start a new multiline tag
			if keyval[0].startswith(";;"):
				multiline = True
				current_multikey = keyval[0].replace(";;", "", 1)
				if not current_multikey in input_replaces:
					input_replaces[current_multikey] = ""
			# If it's not, continue the current multiline
			elif multiline:
				input_replaces[current_multikey] += keyval[0] + "\n"
			else:
				raise Exception("what")
				
					
					
					
				


def parse_content(content, ext):
	if ext == ".textile":
		return textile.textile(content)
	elif ext == ".md":
		return pypandoc.convert_text(content, "html5", format="md")
	else:
		raise Exception("Can't recognize the extension in " + os.join(subdir, file))
		return ""