from docutils import nodes
from sphinx.util.docutils import SphinxDirective
from sphinx.util.osutil import copyfile
import os
import re


class consoleoutput_block(nodes.literal_block):
	pass


class ConsoleOutput(SphinxDirective):

	COLOR_CSS_MAP = {
		"i": "white",
		"g": "green",
		"y": "yellow",
		"bl": "blue",
		"r": "red",
		"c": "cyan",
		"b": "bold"
	}

	has_content = True

	def prompt(self, inline_stack, kind="#", highlight=True, hostname=None):
		"""
		This will yield elements to Sphinx to render a prompt. It will also initialize ``inline_stack`` with
		an inline element that will highlight user input by default.

		This method is written generator-style to yield elements. If ``highlight`` is True, we will keep a
		'highlight' element on ``inline_stack`` so that further input on this line will be highlighted as
		user input. This is the default behavior.
		"""

		prompt_one = nodes.inline()
		if hostname:
			prompt_one['classes'].append('ansi-yellow')
			prompt_one['classes'].append('ansi-bold')
			prompt_one.append(nodes.Text(f"{hostname}"))
		elif kind == "#":  # root
			prompt_one['classes'].append('ansi-red')
			prompt_one['classes'].append('ansi-bold')
			prompt_one.append(nodes.Text("root"))
		elif kind == "$":  # user
			prompt_one['classes'].append('ansi-green')
			prompt_one['classes'].append('ansi-bold')
			prompt_one.append(nodes.Text("user"))
		yield prompt_one

		# Add '$' or '#' to output:
		prompt_two = nodes.inline()
		prompt_two['classes'].append('ansi-blue')
		prompt_two['classes'].append('ansi-bold')
		prompt_two.append(nodes.Text(f" {kind}"))
		yield prompt_two

		# Auto-enable highlighting:
		if highlight is True:
			inline = nodes.inline()
			inline['classes'].append('ansi-bold')
			inline_stack.append(inline)

	def expand_codes(self, inline_stack, line):
		"""
		This method does the heavy lifting of converting a line to a potentially nested set of inline
		elements with the proper classes applied, and yielding these Sphinx elements back in the proper
		order for Sphinx to render them.

		In order to do this correctly, we internally create a stack of active inline elements. This is
		done in ``inline_stack``. If there are items in ``inline_stack``, then ``inline_stack[-1]``
		represents the currently-active inline element to which we will add text (or new inline elements
		if we have nested color sections).

		When we create a new Sphinx inline element, we will make it the new currently-active inline
		element, and also link it to any previously-active inline element. This means that the 'master'
		(bottom) element in the stack already contains the higher elements.

		When the method returns, it will be sure to yield the 'master' (bottom) element of the stack,
		since this item will hold "all the things" (child inline elements and text) already.

		There might be other stuff still in the stack. We can ignore these things. They are already
		linked into the 'master' element and are just leftover 'internal accounting information'.
		If there is leftover stuff in the stack, it's due to some colors being "started" but no
		"closing" tags ``("##!?##")`` appearing on the line. This is okay.

		This method is a 'generator style', and will yield things in the order they should be written
		to the output by Sphinx. The method can yield nodes.Text elements, and will yield the master
		('bottom') element from the stack. No trailing newline will be included in the output.
		"""
		pos = 0
		found = re.split(f'(##!?[a-z][a-z]?##)', line)
		while pos < len(found):
			if not found[pos].startswith("##"):
				# regular text
				if not len(inline_stack):
					yield nodes.Text(found[pos])
				else:
					inline_stack[-1].append(nodes.Text(found[pos]))
			elif found[pos].startswith("##!"):
				# ending color code
				code = found[pos].strip("#")[1:]
				if not len(inline_stack) or inline_stack[-1] != code:
					yield nodes.Text("Error -- nesting mismatch.")
					break
				inline = inline_stack.pop()
				if not len(inline_stack):
					# We popped the bottom of the stack. Return master inline element to caller.
					yield inline
			else:
				inline_code = found[pos].strip("#")
				if inline_code not in self.COLOR_CSS_MAP:
					yield nodes.Text("Error -- invalid color code")
					break
				inline = nodes.inline()
				inline['classes'].append(f"ansi-{self.COLOR_CSS_MAP[inline_code]}")
				if len(inline_stack):
					# Put our new inline "inside" an existing inline for Sphinx:
					inline_stack[-1].append(inline)
				inline_stack.append(inline)
			pos += 1
		if len(inline_stack):
			# return only the "bottom" item in our stack since all others will be nested in it already.
			yield inline_stack[0]

	def run(self):
		# The rawsource='' hack should hopefully disable syntax highlighting...
		block = consoleoutput_block(rawsource='')
		block['classes'].append('ansi-block')
		block['highlight'] = None

		lines = self.content
		for line in lines:
			inline_stack = []
			# Add a prompt, and by default highlight the rest of the text as input:
			highlight = True
			if len(line) and line[0] in "#$":
				kind = line[0]
				hostname = None
				if len(line) > 3 and line[1] == "%":  # hostname
					other = line[2:].find('%')
					if other != -1:
						# add extra +2 to end positions due to our find looking from 2 position:
						hostname = line[2:other+2]
						line = line[other+3:]
				else:
					line = line[1:]
				block.extend(list(self.prompt(inline_stack, kind=kind, hostname=hostname, highlight=highlight)))
			# This adds the rest of the line to the output
			block.extend(list(self.expand_codes(inline_stack, line)))
			block.append(nodes.Text("\n"))
		return [block]


def add_stylesheet(app):
	app.add_css_file("consoleoutput.css")


def copy_stylesheet(app, exception):
	dest = os.path.join(app.builder.outdir, '_static', 'consoleoutput.css')
	source = os.path.join(os.path.abspath(os.path.dirname(__file__)), '_static', 'consoleoutput.css')
	os.makedirs(os.path.dirname(dest), exist_ok=True)
	copyfile(source, dest)


def setup(app):
	app.add_directive("console", ConsoleOutput)
	app.connect('builder-inited', add_stylesheet)
	app.connect('build-finished', copy_stylesheet)

	return {
		'version': '0.1',
		'parallel_read_safe': True,
		'parallel_write_safe': True,
	}

# vim: ts=4 sw=4 noet
