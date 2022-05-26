#!/usr/bin/env python3

import urwid

from . import model_input_history

class EditWithHistory(urwid.Edit):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.history = model_input_history.History()
		self.command_map = self._command_map.copy()
		self._command_map = self._command_map.copy()
		self._command_map.clear_command(urwid.CURSOR_UP)
		self._command_map.clear_command(urwid.CURSOR_DOWN)

	def keypress(self, size, key):
		if not super().keypress(size, key):
			return None

		cmd = self.command_map[key]

		if cmd == urwid.CURSOR_UP:
			if self.history.stash_and_prev(self.edit_text, self.edit_pos):
				self.edit_text = self.history.get_text()
				self.edit_pos = self.history.get_cursor_position()
			return None

		elif cmd == urwid.CURSOR_DOWN:
			if self.history.stash_and_next(self.edit_text, self.edit_pos):
				self.edit_text = self.history.get_text()
				self.edit_pos = self.history.get_cursor_position()
			return None

		if cmd == urwid.ACTIVATE:
			self.history.commit(self.edit_text, self.edit_pos)
			return key

		return key

	def get_last_input(self):
		return self.history.get_text()


if __name__ == '__main__':
	def keypress(key):
		if key == 'esc':
			raise urwid.ExitMainLoop()
		elif urwid.command_map[key] == urwid.ACTIVATE:
			edit.edit_text = ""
		else:
			statusbar.set_text("unhandled key: %s" % key)

	edit = EditWithHistory()
	widget = urwid.Filler(edit)
	statusbar = urwid.Text("")
	frame = urwid.Frame(widget, footer=statusbar)
	urwid.MainLoop(frame, unhandled_input=keypress).run()
