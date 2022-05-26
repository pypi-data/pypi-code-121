#!/usr/bin/env python3

import urwid
calc_width = urwid.util.calc_width
calc_text_pos = urwid.util.calc_text_pos
move_next_char = urwid.util.move_next_char
move_prev_char = urwid.util.move_prev_char


def reverse_calc_text_pos(text, i0, i1, max_width):
	'''
	return (i, sc)
	where i is the smallest text index with i0 <= i <= i1
	so that text[i:i1] takes up as many screen column sc
	as possible with sc <= max_width. (If text contains
	full width characters sc may be smaller than max_width.)
	'''
	sc = 0
	while sc < max_width and i1 > i0:
		i = move_prev_char(text, i0, i1)
		char_width = calc_width(text, i, i1)
		if sc + char_width > max_width:
			break
		i1 = i
		sc += char_width
	return i1, sc


class LogTextLayout(urwid.StandardTextLayout):

	"""
	Extends the StandardTextLayout by a new align mode:
	ALIGN_INDENTATION

	In this mode text will be printed left aligned
	with the first line starting at the very left
	and the following lines indented.
	The indentation is specified by the first occurence
	of align_character in each printed line. This first
	occurence of align_character is hidden.
	Spaces directly following the align_character become
	part of the indentation as well because the %d place
	holder of git log expands to either nothing or some
	thing starting with " (" so that it is not possible
	to put the align_character after the space.

	Also extends the StandardTextLayout by a new wrap mode:
	WRAP_CUSTOM

	This is a generalization of WRAP_SPACE. The characters
	after which a break is allowed can be specified with
	wrap_after_characters.
	"""

	ALIGN_LEFT = urwid.LEFT
	ALIGN_RIGHT = urwid.RIGHT
	ALIGN_CENTER = urwid.CENTER
	ALIGN_INDENTATION = "left indentation"
	ALLOWED_ALIGN_VALUES = (ALIGN_LEFT, ALIGN_RIGHT, ALIGN_CENTER, ALIGN_INDENTATION)

	WRAP_ANY   = urwid.ANY
	WRAP_SPACE = urwid.SPACE
	WRAP_CLIP  = urwid.CLIP
	WRAP_ELLIPSIS = 'ellipsis'
	WRAP_CUSTOM   = 'custom'
	ALLOWED_WRAP_VALUES = (WRAP_ANY, WRAP_SPACE, WRAP_CLIP, WRAP_ELLIPSIS, WRAP_CUSTOM)

	# minimum number of screen columns for displaying text (with ALIGN_INDENTATION)
	# If the window is too small to show indentation + MIN_WIDTH the indentation is omitted.
	# This value must be greater than 1. Otherwise full width characters and everything after them
	# will not be display if the window has a width of indentation + 1.
	MIN_WIDTH = 2

	EXPLICIT_SPACES = False

	def __init__(self, align_character, ellipsis_character="…".encode('utf-8'), wrap_after_characters="- ", wrap_before_characters=" ", repeat_prefix=False, auto_move_align_character=True):
		"""
		- align_character [for align=ALIGN_INDENTATION]:
		  a string marking how for to indent the following lines
		- ellipsis_character [for wrap=WRAP_ELLIPSIS]:
		  a string to be appended to lines which are clipped because they are too long
		- wrap_after_characters [for wrap=WRAP_CUSTOM]:
		  lines can be wrapped after any character in this string
		- wrap_before_characters [for wrap=WRAP_CUSTOM]:
		  lines can be wrapped before any character in this string
		- repeat_prefix [for align=ALIGN_INDENTATION]:
		  False: broken lines are indented by inserting spaces
		  True: broken lines are indented by inserting the beginning of the text before align_character
		- auto_move_align_character [for align=ALIGN_INDENTATION]:
		  True: treat all space characters directly following the align_character as being before the align_character
		  False: take the position of the align_character literally
		"""
		super().__init__()
		self.align_character = align_character
		if isinstance(ellipsis_character, str):
			self.ellipsis_character = urwid.compat.B(ellipsis_character)
		else:
			self.ellipsis_character = ellipsis_character
		self.width_ellipsis_character = calc_width(ellipsis_character, 0, len(ellipsis_character))
		self.wrap_after_characters = wrap_after_characters
		self.wrap_before_characters = wrap_before_characters
		self.repeat_prefix = repeat_prefix
		self.auto_move_align_character = auto_move_align_character

	def copy(self, **kw):
		for arg in ('align_character', 'ellipsis_character', 'wrap_after_characters', 'wrap_before_characters', 'repeat_prefix', 'auto_move_align_character'):
			kw.setdefault(arg, getattr(self, arg))
		return type(self)(**kw)

	def layout(self, text, width, align, wrap):
		if align == self.ALIGN_INDENTATION:
			segs = self.calculate_text_segments_align(text, width, wrap)
			return self.align_layout(text, width, segs, wrap, self.ALIGN_LEFT)
		if wrap == self.WRAP_CUSTOM:
			segs = self.calculate_text_segments_align(text, width, wrap)
			return self.align_layout(text, width, segs, wrap, align)
		else:
			return super().layout(text, width, align, wrap)

	def calculate_text_segments_align(self, text, width, wrap):
		if wrap == self.WRAP_SPACE:
			wrap_after_characters = " "
			wrap_before_characters = " "
			wrap = self.WRAP_CUSTOM
		else:
			wrap_after_characters = self.wrap_after_characters
			wrap_before_characters = self.wrap_before_characters

		# ----- str vs bytes -----
		nl = "\n"
		align_character = self.align_character
		if urwid.compat.PYTHON3 and isinstance(text, bytes):
			nl = urwid.compat.B(nl)
			align_character = urwid.compat.B(align_character)
			wrap_after_characters = urwid.compat.B(wrap_after_characters)
			wrap_before_characters = urwid.compat.B(wrap_before_characters)
		wrap_after_characters += nl
		wrap_before_characters += nl

		# ----- align_character & indentation -----
		n = len(text)
		trailing_linebreaks = 0
		while text[n-1:n] == nl:
			trailing_linebreaks += 1
			n -= 1

		align_character_i0 = text.find(align_character)
		if align_character_i0 == -1:
			width_indent = 0
			align_character_i1 = -1
		else:
			align_character_i1 = align_character_i0 + len(align_character)
			i = text.rfind(nl, 0, align_character_i1)
			if i >= 0:
				i += 1
			else:
				i = 0
			width_indent = calc_width(text, i, align_character_i0)
			indent_i0 = i

			if self.auto_move_align_character:
				i1 = align_character_i1
				while text[i1:i1+1].isspace() and not text[i1:i1+1] == nl:
					i1 = move_next_char(text, i1, n)
				width_indent0 = width_indent
				width_indent1 = calc_width(text, align_character_i1, i1)
				width_indent = width_indent0 + width_indent1
				indent_i1 = i1
			else:
				width_indent0 = width_indent
				width_indent1 = 0
				indent_i1 = align_character_i1

			if width < width_indent + self.MIN_WIDTH:
				width_indent = 0

		# ----- process text -----
		layout_struct = []
		i0 = 0

		current_width = width
		current_indentation = 0
		while i0 < n:
			last_i0 = i0
			ln = []
			layout_struct.append(ln)

			# insert indentation
			if current_indentation:
				if self.repeat_prefix:
					if width_indent0:
						ln.append((width_indent0, indent_i0, align_character_i0))
					if width_indent1:
						ln.append((width_indent1, align_character_i1, indent_i1))
				elif self.EXPLICIT_SPACES:
					ln.append((current_indentation, i0, b" "*current_indentation))
				else:
					ln.append((current_indentation, None))

			# find end of line, by \n or lack of space
			i1 = text.find(nl, i0)
			if i1 == -1:
				i1 = n
			i1, sc = calc_text_pos(text, i0, i1, current_width)
			assert i1 >= i0

			# hide align_character
			if i0 <= align_character_i0 < i1:
				sc = calc_width(text, i0, align_character_i0)
				if sc:
					ln.append((sc, i0, align_character_i0))
				i0 = align_character_i1

				# move i1 right to make up for ignored align_character
				# I am starting at i0 to get the correct number of screen columns
				assert current_indentation == 0
				i = text.find(nl, i0)
				if i < 0:
					i = n
				i1, sc = calc_text_pos(text, i0, i, current_width-sc)

				current_indentation = width_indent
				current_width = width - current_indentation

			# apply wrap
			if i1 >= n or wrap == self.WRAP_CLIP:
				if sc:
					ln.append((sc, i0, i1))
				break
			elif wrap == self.WRAP_ELLIPSIS:
				if sc:
					ln.append((sc, i0, i1))
				self.add_ellipsis_character(text, ln, width)
				break
			elif text[i1:i1+1] == nl:
				if sc:
					ln.append((sc, i0, i1))
				i1 += 1
				i0 = i1
				continue
			elif wrap == self.WRAP_ANY:
				pass
			elif wrap == self.WRAP_CUSTOM:
				i = i1
				i1_min = i0 + 1
				while i > i1_min and text[i-1:i] not in wrap_after_characters and text[i:i+1] not in wrap_before_characters:
					i = move_prev_char(text, i1_min, i)
				if i > i1_min and not text[i0:i].isspace():
					i1 = i
				sc = calc_width(text, i0, i1)

			else:
				raise ValueError("invalid value for wrap: %s" % wrap)

			# add line
			if sc:
				ln.append((sc, i0, i1))

			while text[i1:i1+1].isspace():
				i1 = move_next_char(text, i1, n)

			# preprare processing of next line
			i0 = i1

			# stop if no progress has been made to avoid an infinite loop if window is too narrow
			if i0 == last_i0:
				break

		for i in range(trailing_linebreaks):
			layout_struct.append([])

		if not layout_struct:
			layout_struct.append([])

		return layout_struct

	def add_ellipsis_character(self, text, ln, width):
		if self.width_ellipsis_character > width:
			i0, sc = reverse_calc_text_pos(self.ellipsis_character, 0, len(self.ellipsis_character), width)
			ln.clear()
			ln.append((sc, 0, self.ellipsis_character[i0:]))
			return

		remaining_width = width - self.width_ellipsis_character
		ln_sc = sum(ts[0] for ts in ln)

		if ln_sc > remaining_width:
			assert ln
			while ln_sc > remaining_width:
				ts = ln[-1]
				del ln[-1]
				ln_sc -= ts[0]

			remaining_width -= ln_sc

			if len(ts) == 2:
				sc, i = ts
				ts = (remaining_width, i)
			elif isinstance(ts[2], int):
				sc, i0, i1 = ts
				i1, sc = calc_text_pos(text, i0, i1, remaining_width)
				ts = (sc, i0, i1)
			else:
				sc, i, insert_text = ts
				i1, sc = calc_text_pos(insert_text, 0, len(insert_text), remaining_width)
				ts = (sc, i, insert_text[:i1])

			if ts[0]:
				ln.append(ts)

		if not ln:
			i = 0
		else:
			i = ln[-1][1]

		if self.width_ellipsis_character:
			ln.append((self.width_ellipsis_character, i, self.ellipsis_character))

	def supports_align_mode(self, align):
		if align == self.ALIGN_INDENTATION:
			return True

		return super().supports_align_mode(align)

	def supports_wrap_mode(self, wrap):
		if wrap == self.WRAP_CUSTOM:
			return True

		return super().supports_wrap_mode(wrap)


WRAP = LogTextLayout.WRAP_SPACE
ALIGN = LogTextLayout.ALIGN_INDENTATION
