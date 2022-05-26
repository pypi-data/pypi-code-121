#!/usr/bin/env python3

from . import urwid_constants
from . import color_decoder

CD = color_decoder.ColorDecoder
COLOR = urwid_constants.COLOR

default_foreground_color = {
	CD.FG_DEFAULT: COLOR.FG_DEFAULT,
}

standard_foreground_colors = {
	CD.FG_BLACK:   COLOR.FG_BLACK,
	CD.FG_RED:     COLOR.FG_RED,
	CD.FG_GREEN:   COLOR.FG_GREEN,
	CD.FG_YELLOW:  COLOR.FG_YELLOW,
	CD.FG_BLUE:    COLOR.FG_BLUE,
	CD.FG_MAGENTA: COLOR.FG_MAGENTA,
	CD.FG_CYAN:    COLOR.FG_CYAN,
	CD.FG_GRAY:    COLOR.FG_WHITE,
}

light_foreground_colors = {
	CD.FG_LIGHT_BLACK:   COLOR.FG_BRIGHT_BLACK,
	CD.FG_LIGHT_RED:     COLOR.FG_BRIGHT_RED,
	CD.FG_LIGHT_GREEN:   COLOR.FG_BRIGHT_GREEN,
	CD.FG_LIGHT_YELLOW:  COLOR.FG_BRIGHT_YELLOW,
	CD.FG_LIGHT_BLUE:    COLOR.FG_BRIGHT_BLUE,
	CD.FG_LIGHT_MAGENTA: COLOR.FG_BRIGHT_MAGENTA,
	CD.FG_LIGHT_CYAN:    COLOR.FG_BRIGHT_CYAN,
	CD.FG_LIGHT_GRAY:    COLOR.FG_BRIGHT_WHITE,
}

default_background_color = {
	CD.BG_DEFAULT: COLOR.BG_DEFAULT,
}

background_colors = {
	CD.BG_BLACK:   COLOR.BG_BLACK,
	CD.BG_RED:     COLOR.BG_RED,
	CD.BG_GREEN:   COLOR.BG_GREEN,
	CD.BG_YELLOW:  COLOR.BG_YELLOW,
	CD.BG_BLUE:    COLOR.BG_BLUE,
	CD.BG_MAGENTA: COLOR.BG_MAGENTA,
	CD.BG_CYAN:    COLOR.BG_CYAN,
	CD.BG_GRAY:    COLOR.BG_WHITE,
}

series = {
	CD.NORMAL : "",
	CD.BOLD   : urwid_constants.EMPH.BOLD,
}


class Generator:

	"""
	Create a pallete which maps the color_decoder names to urwid colors.

	For efficiency reasons not all possible combinations are created
	by default. You can use the arguments of the constructor to select
	which colors/formats you need.

	If you set fg to True and bg to True all possible combinations
	between the two will be created.
	If you want to have foreground colors on the default background
	and the default foreground on background colors but not all
	possible combinations of foreground and background colors
	use two Generator objects (where one has fg=True, bg=False and
	one has fg=False, bg=True) and add their output.
	"""

	FOCUS_SUFFIX = "_focus"

	def __init__(self, bold=True, standard_fg=True, light_fg=False, bg=False, focus=True):
		self.activated_series = [CD.NORMAL]
		if bold:
			self.activated_series.append(CD.BOLD)

		self.activated_fg_colors = default_foreground_color
		if standard_fg:
			self.activated_fg_colors.update(standard_foreground_colors)
		if light_fg:
			self.activated_fg_colors.update(light_foreground_colors)

		self.activated_bg_colors = default_background_color
		if bg:
			self.activated_bg_colors.update(background_colors)

		self.focus = focus


	def palette(self):
		out = list()

		for series_decoder_name in self.activated_series:
			for bg_decoder_name, bg_urwid_name in self.activated_bg_colors.items():
				for fg_decoder_name, fg_urwid_name in self.activated_fg_colors.items():
					name = CD.combine_colors(series_decoder_name, fg_decoder_name, bg_decoder_name)
					if series_decoder_name == CD.BOLD:
						fg_urwid_name += urwid_constants.EMPH.BOLD
					out.append((name, fg_urwid_name, bg_urwid_name))

					if self.focus:
						name += self.FOCUS_SUFFIX
						fg_urwid_name += urwid_constants.EMPH.STANDOUT
						out.append((name, fg_urwid_name, bg_urwid_name))

		return out


	def focus_map(self):
		out = dict()

		for series_decoder_name in self.activated_series:
			for bg_decoder_name, bg_urwid_name in self.activated_bg_colors.items():
				for fg_decoder_name, fg_urwid_name in self.activated_fg_colors.items():
					name = CD.combine_colors(series_decoder_name, fg_decoder_name, bg_decoder_name)
					out[name] = name + self.FOCUS_SUFFIX

		return out


if __name__ == '__main__':
	g = Generator()
	palette = g.palette()

	import sys
	lines = []
	for fn in sys.argv[1:]:
		with open(fn, 'rt') as f:
			lines.extend(f.readlines())

	if lines:
		# test usage:
		# $ python urwid_color_encoder.py <(colortest)
		# should look pretty much the same like
		# $ colortest

		import urwid

		def quit(key):
			if key.lower() == 'q':
				raise urwid.ExitMainLoop()

		focus_map = g.focus_map()
		decoder = color_decoder.ColorDecoder()
		view = urwid.ListBox([urwid.AttrMap(urwid.SelectableIcon(decoder.decode(ln.rstrip()) + ['']), None, focus_map=focus_map) for ln in lines])
		urwid.MainLoop(view, palette=palette, unhandled_input=quit).run()
	
	else:
		print("\n".join("%-30s, %-30s, %-30s" %(i) for i in palette))
