#!/usr/bin/env python3

"""
It does not seem to be possible to pass through colors in urwid or curses.
Therefore ColorDecoder.decode translates a string containing ansi color
escape sequences into a list of tuples (<colorname>, <text>).
(Even though it sounds a little like the raw_display might support color
 pass through, it does not. In fact, it is the default screen.)

Please note that the returned list can be empty
because tuples are dropped if <text> is empty.
Passing an empty list to an urwid Text widget
causes an Exception.

Implemented escape sequences are:
- foreground colors (3[0-7])
- background colors (4[0-7])
- bright foreground (9[0-7])
- reset (empty)
- bold (1)
https://stackoverflow.com/a/33206814
"""

import re

class ColorDecoder():

	# ---------- input ---------

	# matches:
	#     [m       (reset)
	#     [1m      (bold)
	#     [31m     (red)
	#     [1;31m   (light red)
	# invalid:
	#     [131m
	#
	# so in general I want to match
	# `a`, `b` and `a;b` but not `ab`.
	# I cannot use `a|b|a;b` because
	# `a` and `b` contain named groups.
	# Instead I'm adding a lookahead to
	# `a` (series) that the next character
	# must not be a number.
	reo_color_code = re.compile(
		r'\['
		r'((?P<series>[01])(?![0-9]))?'
		r';?'
		r'((?P<fgbg>[349])(?P<color>[0-79]))?'
		r'm'
	)

	NORMAL = '0'
	BOLD   = '1'

	FOREGROUND = '3'
	BACKGROUND = '4'
	FOREGROUND_LIGHT = '9'

	COLOR_DEFAULT = '9'
	COLOR_BLACK   = '0'
	COLOR_RED     = '1'
	COLOR_GREEN   = '2'
	COLOR_YELLOW  = '3'
	COLOR_BLUE    = '4'
	COLOR_MAGENTA = '5'
	COLOR_CYAN    = '6'
	COLOR_GRAY    = '7'


	# ---------- output ---------

	FG_DEFAULT       = 'default'

	FG_BLACK         = 'black'
	FG_RED           = 'red'
	FG_GREEN         = 'green'
	FG_YELLOW        = 'yellow'
	FG_BLUE          = 'blue'
	FG_MAGENTA       = 'magenta'
	FG_CYAN          = 'cyan'
	FG_GRAY          = 'gray'

	FG_LIGHT_BLACK   = 'dark gray'
	FG_LIGHT_RED     = 'light red'
	FG_LIGHT_GREEN   = 'light green'
	FG_LIGHT_YELLOW  = 'light yellow'
	FG_LIGHT_BLUE    = 'light blue'
	FG_LIGHT_MAGENTA = 'light magenta'
	FG_LIGHT_CYAN    = 'light cyan'
	FG_LIGHT_GRAY    = 'white'


	BG_DEFAULT = 'default'

	BG_BLACK   = 'black'
	BG_RED     = 'red'
	BG_GREEN   = 'green'
	BG_YELLOW  = 'yellow'
	BG_BLUE    = 'blue'
	BG_MAGENTA = 'magenta'
	BG_CYAN    = 'cyan'
	BG_GRAY    = 'gray'


	# ---------- mapping ---------

	decode_map = {
		FOREGROUND : {
			COLOR_DEFAULT : FG_DEFAULT,
			COLOR_BLACK   : FG_BLACK,
			COLOR_RED     : FG_RED,
			COLOR_GREEN   : FG_GREEN,
			COLOR_YELLOW  : FG_YELLOW,
			COLOR_BLUE    : FG_BLUE,
			COLOR_MAGENTA : FG_MAGENTA,
			COLOR_CYAN    : FG_CYAN,
			COLOR_GRAY    : FG_GRAY,
		},
		FOREGROUND_LIGHT : {
			COLOR_BLACK   : FG_LIGHT_BLACK,
			COLOR_RED     : FG_LIGHT_RED,
			COLOR_GREEN   : FG_LIGHT_GREEN,
			COLOR_YELLOW  : FG_LIGHT_YELLOW,
			COLOR_BLUE    : FG_LIGHT_BLUE,
			COLOR_MAGENTA : FG_LIGHT_MAGENTA,
			COLOR_CYAN    : FG_LIGHT_CYAN,
			COLOR_GRAY    : FG_LIGHT_GRAY,
		},
		BACKGROUND : {
			COLOR_DEFAULT : BG_DEFAULT,
			COLOR_BLACK   : BG_BLACK,
			COLOR_RED     : BG_RED,
			COLOR_GREEN   : BG_GREEN,
			COLOR_YELLOW  : BG_YELLOW,
			COLOR_BLUE    : BG_BLUE,
			COLOR_MAGENTA : BG_MAGENTA,
			COLOR_CYAN    : BG_CYAN,
			COLOR_GRAY    : BG_GRAY,
		},
	}

	@staticmethod
	def combine_colors(series, fg, bg):
		return "%s-%s:%s" % (series, fg, bg)


	# ---------- instance methods ---------

	def __init__(self):
		self.reset()

	def reset(self):
		self.color_fg = self.COLOR_DEFAULT
		self.color_bg = self.COLOR_DEFAULT
		self.series = self.NORMAL
		self.foreground = self.FOREGROUND
		self.background = self.BACKGROUND
	
	def decode(self, text):
		out = []

		i = None
		color = self.get_current_color()
		for m in self.reo_color_code.finditer(text):
			self.apply_color(m)

			subtext = text[i:m.start()]
			if subtext:
				out.append((color, subtext))

			color = self.get_current_color()
			i = m.end()

		subtext = text[i:]
		if subtext:
			out.append((color, subtext))

		return out

	def apply_color(self, color_code_match):
		m = color_code_match

		fgbg = m.group("fgbg")
		color = m.group("color")
		series = m.group("series")

		if fgbg is None and series is None:
			self.reset()

		if fgbg == self.FOREGROUND or fgbg == self.FOREGROUND_LIGHT:
			self.color_fg = color
			self.foreground = fgbg
		elif fgbg == self.BACKGROUND:
			self.color_bg = color
			self.background = fgbg

		if series is not None:
			self.series = series
	
	def get_current_color(self):
		fg = self.decode_map[self.foreground][self.color_fg]
		bg = self.decode_map[self.background][self.color_bg]
		return self.combine_colors(self.series, fg, bg)


if __name__ == '__main__':
	import sys

	decoder = ColorDecoder()

	if len(sys.argv) <= 1 or sys.argv[1] == '--full':
		for ln in sys.stdin.readlines():
			l = decoder.decode(ln)
			print(l)

	else:
		colors = set()
		for ln in sys.stdin.readlines():
			l = decoder.decode(ln)
			for color, text in l:
				colors.add(color)

		print("\n".join(sorted(colors)))
