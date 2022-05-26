#!/usr/bin/env python3

import re
import gettext
_ = gettext.gettext

from . import urwid_constants


# ------- create table -------

def format_table(rows, *, fmt='%s', col_sep=" "):
	if not rows:
		return ""

	num_cols = len(rows[0])
	num_rows = len(rows)
	if not isinstance(fmt, list):
		fmt = [fmt] * num_cols
	else:
		while len(fmt) < num_cols:
			fmt.append('%s')

	rows = [[f%cell for cell,f in zip(row,fmt)] for row in rows]
	col_widths = [len(max((rows[row][col] for row in range(num_rows)), key=len)) for col in range(num_cols)]
	return [col_sep.join(cell.ljust(w) for cell,w in zip(row,col_widths)) for row in rows]


# ------- lists -------

def replace_to_markup(ln:str, old:str, new, *, count:int=-1, markup_function=None) -> list:
	if not isinstance(new, list):
		new = [new]

	out = []
	first = True
	for word in ln.split(old, count):
		if first:
			first = False
		else:
			out.extend(new)

		if not word:
			continue

		if markup_function:
			word = markup_function(word)

		if isinstance(word, list):
			out.extend(word)
		else:
			out.append(word)

	return out

def iter_join(sep, iterable):
	iterable = iter(iterable)
	try:
		yield next(iterable)
		for item in iterable:
			yield sep
			yield item
	except StopIteration:
		pass

def list_join(sep, iterable):
	return list(iter_join(sep, iterable))


# ------- replace in markup -------

def replace_in_markup(markup, old, new):
	'''
	old: regular expression object
	new: markup or function which takes a match object and returns a markup
	in contrast to replace_attribute this replaces text, no attributes
	'''
	if isinstance(old, str):
		old = re.compile(re.escape(old))

	if isinstance(markup, str):
		return replace_in_str(markup, old, new)

	if isinstance(markup, tuple):
		assert len(markup) == 2
		return (markup[0], replace_in_markup(markup[1], old, new))

	out = []
	for w in markup:
		out.append(replace_in_markup(w, old, new))
	return out

def replace_in_str(markup: str, old, new):
	out = []
	def append(w):
		if w is None:
			raise TypeError("new returns None")
		if not w:
			return
		if isinstance(w, str) and out and isinstance(out[-1], str):
			out[-1] += w
			return
		out.append(w)
	i = 0
	for m in old.finditer(markup):
		append(markup[i:m.start()])
		try:
			w = new(m)
		except TypeError:
			w = new
		if isinstance(w, list):
			for wi in w: append(wi)
		else:
			append(w)
		i = m.end()
	append(markup[i:])

	if not out:
		return ""

	if isinstance(out, list) and len(out) == 1:
		return out[0]

	return out

# ------- simplify markup -------

def simplify_markup(markup):
	'''clean up the markup to avoid bugs in urwid'''
	if isinstance(markup, str):
		return markup
	
	out = list(_simplify_markup(None, markup))
	if not out:
		return ""
	
	if len(out) == 1:
		return out[0]
	
	return out

def _simplify_markup(default_attribute, markup):
	if isinstance(markup, str):
		yield (default_attribute, markup)
	
	elif isinstance(markup, tuple):
		yield from _simplify_markup(markup[0], markup[1])
	
	else:
		last_attr = None
		last_markups = []
		for m in markup:
			for ia, im in _simplify_markup(default_attribute, m):
				if ia != last_attr:
					if last_markups:
						yield last_attr, "".join(last_markups)
					last_attr = ia
					last_markups = []
				last_markups.append(im)
		if last_markups:
			yield last_attr, "".join(last_markups)

# ------- replace attributes -------

def replace_attribute(markup, attr, newattr):
	'''
	replace attr in markup with newattr, returns (newmarkup, number of replacements)
	in contrast to replace_in_markup this replaces attributes, no text
	'''
	assert isinstance(attr, str)
	assert isinstance(newattr, str)
	if isinstance(markup, str):
		return markup, 0
	if isinstance(markup, tuple):
		markup1, n = replace_attribute(markup[1], attr, newattr)
		if markup[0] == attr:
			return (newattr, markup1), n+1
		else:
			return (markup[0], markup1), n

	out = []
	n = 0
	for m in markup:
		_m, _n = replace_attribute(m, attr, newattr)
		out.append(_m)
		n += _n
	return out, n

# ------- palette tuples <-> color strings -------

SEP_COLOR = "/"
ALLOWED_EMPHASIS = {"bold", "underline", "standout", "italics", "blink", "strikethrough"}

def palette_tuple_to_color_str(palette_tuple):
	name, fg, bg = palette_tuple
	fg = _convert_fg_to_user(fg)
	bg = _convert_bg_to_user(bg)
	return fg + SEP_COLOR + bg

def _convert_fg_to_user(fg):
	fg = fg.split(",")
	fg_color = fg[0]
	for name, value in urwid_constants.COLOR.__dict__.items():
		if name.startswith("FG_") and value == fg_color:
			fg_color = name[3:].lower().replace("_", " ")
			fg[0] = fg_color
			fg = ",".join(fg)
			return fg

	assert False, "INTERNAL ERROR: invalid foreground color %r" % fg

def _convert_bg_to_user(bg):
	bg = bg.split(",")
	bg_color = bg[0]
	for name, value in urwid_constants.COLOR.__dict__.items():
		if name.startswith("FG_") and value == bg_color:
			bg_color = name[3:].lower().replace("_", " ")
			bg[0] = bg_color
			bg = ",".join(bg)
			return bg

	assert False, "INTERNAL ERROR: invalid background color %r" % bg


def color_str_to_palette_tuple(name, color_str):
	if SEP_COLOR in color_str:
		fg, bg = color_str.split(SEP_COLOR, 1)
	else:
		fg = color_str
		bg = urwid_constants.COLOR.BG_DEFAULT

	fg = _convert_fg_to_urwid(fg)
	bg = _convert_bg_to_urwid(bg)

	return (name, fg, bg)

def _convert_fg_to_urwid(fg):
	fg = fg.split(",")
	fg_color = "FG_" + fg[0].upper().replace(" ", "_")
	fg_color = getattr(urwid_constants.COLOR, fg_color, None)
	if fg_color is None:
		raise ValueError(_("invalid foreground color %r") % fg[0])
	for i in range(1, len(fg)):
		if fg[i] not in ALLOWED_EMPHASIS:
			raise ValueError(_("invalid emphasis %r") % fg[i])

	fg[0] = fg_color
	return ",".join(fg)

def _convert_bg_to_urwid(bg):
	bg_color = "BG_" + bg.upper().replace(" ", "_")
	bg_color = getattr(urwid_constants.COLOR, bg_color, None)
	if bg_color is None:
		raise ValueError(_("invalid background color %r") % bg)
	return bg_color


# ------- color markup -------

_reo_color_tag = re.compile(r'<color=([^>]*)>|</color>')
def colored_str_to_markup(coloredstr, define_color):
	# >>> colored_str_to_markup('hello <color=red>world</color>')
	# l = ['hello ', 'red', 'world', None, '']
	l = _reo_color_tag.split(coloredstr)
	n = len(l)
	out = []

	text = l[0]
	if text:
		out.append(text)

	i = 1
	while i < n:
		i = _colored_str_to_markup(l, i, n, out, define_color)
		assert i % 2 == 1

		if i >= n:
			break

		i += 1
		text = l[i]
		assert isinstance(text, str)

		if text:
			out.append(text)

		i += 1

	if not out:
		return ""

	if len(out) == 1:
		return out[0]

	return out

def _colored_str_to_markup(l, i, n, out, define_color):
	color = l[i]
	assert isinstance(color, str)
	subout = []

	while i < n:
		assert i % 2 == 1

		i += 1
		text = l[i]
		assert isinstance(text, str)

		if text:
			subout.append(text)

		i += 1
		if i >= n or l[i] is None:
			break
		else:
			i = _colored_str_to_markup(l, i, n, subout, define_color)

	if subout:
		if len(subout) == 1:
			subout = subout[0]
		color = define_color(color)
		out.append((color, subout))

	return i


# ------- mnemonics -------

class CommandWithMnemonic(str):

	__slots__ = ('mnemonic')

	def __new__(cls, cmd, mnemonic):
		cmd = super().__new__(cls, cmd)
		cmd.mnemonic = mnemonic
		return cmd

	def __repr__(self):
		return "%s(%s, %r)" % (type(self).__name__, super().__repr__(), self.mnemonic)

	def __add__(self, other):
		if isinstance(other, Mnemonic):
			return CommandWithMnemonic(self, self.mnemonic + Mnemonic.sep + other.mnemonic)
		return super().__add__(other)

class Mnemonic:

	__slots__ = ('mnemonic')
	sep = _(", ")

	def __init__(self, mnemonic):
		self.mnemonic = mnemonic

	def __rfloordiv__(self, cmd):
		assert isinstance(cmd, str)
		return CommandWithMnemonic(cmd, self.mnemonic)

def like_in(*other_programs):
	other_programs = join(other_programs, _(', '), _(' and '))
	mnemonic = _('like in {other_programs}').format(other_programs=other_programs)
	return Mnemonic(mnemonic)

def join(l, sep, last_sep):
	if not l:
		return ""
	last = l[-1]
	l = l[:-1]
	if not l:
		return last
	return last_sep.join((sep.join(l), last))
