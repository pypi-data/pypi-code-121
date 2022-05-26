#!/usr/bin/env python3

import urwid

# see Urwid Documentation, Release 1.3.1
# section 3.8.2 Foreground and Background Settings


class COLOR:

	# ------- foreground -------

	FG_DEFAULT       = 'default'

	FG_BLACK         = 'black'
	FG_RED           = 'dark red'
	FG_GREEN         = 'dark green'
	FG_YELLOW        = 'brown'
	FG_BLUE          = 'dark blue'
	FG_MAGENTA       = 'dark magenta'
	FG_CYAN          = 'dark cyan'
	FG_WHITE         = 'light gray'

	FG_BRIGHT_BLACK   = 'dark gray'
	FG_BRIGHT_RED     = 'light red'
	FG_BRIGHT_GREEN   = 'light green'
	FG_BRIGHT_YELLOW  = 'yellow'
	FG_BRIGHT_BLUE    = 'light blue'
	FG_BRIGHT_MAGENTA = 'light magenta'
	FG_BRIGHT_CYAN    = 'light cyan'
	FG_BRIGHT_WHITE   = 'white'


	# ------- background -------

	BG_DEFAULT = 'default'

	BG_BLACK   = 'black'
	BG_RED     = 'dark red'
	BG_GREEN   = 'dark green'
	BG_YELLOW  = 'brown'
	BG_BLUE    = 'dark blue'
	BG_MAGENTA = 'dark magenta'
	BG_CYAN    = 'dark cyan'
	BG_WHITE   = 'light gray'


class EMPH:

	"""usage: COLOR.FG_* + EMPH.BOLD"""

	BOLD      = ",bold"
	UNDERLINE = ",underline"
	STANDOUT  = ",standout"



if __name__ == '__main__':

	# ------- test -------

	fg_colors = [
		COLOR.FG_BLACK,
		COLOR.FG_RED,
		COLOR.FG_GREEN,
		COLOR.FG_YELLOW,
		COLOR.FG_BLUE,
		COLOR.FG_MAGENTA,
		COLOR.FG_CYAN,
		COLOR.FG_WHITE,
	]

	fg_colors_light = [
		COLOR.FG_LIGHT_BLACK,
		COLOR.FG_LIGHT_RED,
		COLOR.FG_LIGHT_GREEN,
		COLOR.FG_LIGHT_YELLOW,
		COLOR.FG_LIGHT_BLUE,
		COLOR.FG_LIGHT_MAGENTA,
		COLOR.FG_LIGHT_CYAN,
		COLOR.FG_LIGHT_WHITE,
	]

	bg_colors = [
		COLOR.BG_BLACK,
		COLOR.BG_RED,
		COLOR.BG_GREEN,
		COLOR.BG_YELLOW,
		COLOR.BG_BLUE,
		COLOR.BG_MAGENTA,
		COLOR.BG_CYAN,
		COLOR.BG_WHITE,
	]

	def input_handler(key):
		if key == "q" or key == "enter":
			raise urwid.ExitMainLoop()

		return key

	indent = "    "
	exp_text_1 = "hello "
	exp_text_2 = "world"

	widgets = [urwid.Text("foreground colors:")] \
	        + [urwid.Text([indent, ("fg: %s" % col, exp_text_1), ("fg: %s" % col_light, exp_text_2)]) for col, col_light in zip(fg_colors, fg_colors_light)] \
	        + [urwid.Text("")] \
	        + [urwid.Text("background colors:")] \
	        + [urwid.Text([indent, ("bg: %s" % col, exp_text_1 + exp_text_2)]) for col in bg_colors]

	palette = [("fg: %s" % col, col, COLOR.BG_DEFAULT) for col in fg_colors] \
	        + [("fg: %s" % col, col, COLOR.BG_DEFAULT) for col in fg_colors_light] \
	        + [("bg: %s" % col, COLOR.FG_DEFAULT, col) for col in bg_colors]

	listbox = urwid.ListBox(urwid.SimpleFocusListWalker(widgets))
	urwid.MainLoop(listbox, palette=palette, unhandled_input=input_handler).run()
