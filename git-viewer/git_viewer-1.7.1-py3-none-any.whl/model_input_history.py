#!/usr/bin/env python3

class History:

	"""
	There are two different functions to save data: commit and stash.
	For both is true:
	Given text will be saved if it is different from the current text.
	Given cursor position will always be saved.

	Committed text will never be changed.
	Committed cursor position can be changed.

	If the current entry was committed a new stash is inserted after it.
	If the current entry was stashed a new stash overwrites it.

	A commit is always appended to the end.
	All stashed changes are removed on the next commit.
	"""

	# data: list of entries
	# entry: 3-tuple (is_committed: bool, text: str, cursor_position: int)
	KEY_IS_COMMITTED = 0
	KEY_TEXT = 1
	KEY_CURSOR_POSITION = 2

	def __init__(self):
		self.data = [[False, "", 0]]
		self.index = 0

	# ---------- setter ----------

	def commit(self, text, cursor_position):
		"""remove all entries that are not committed and commit the given values"""
		self.data = [entry for entry in self.data if self.is_committed(entry)]
		self.index = self._get_last_index()

		if self.data and text == self.get_text():
			self.data[self.index][self.KEY_CURSOR_POSITION] = cursor_position
		else:
			self.index += 1
			self.data.append([True, text, cursor_position])

	def stash_and_prev(self, text, cursor_position):
		"""save the given values temporarily and select the previous entry"""
		self.stash(text, cursor_position)

		if self.index <= 0:
			return False
		else:
			self.index -= 1
			return True

	def stash_and_next(self, text, cursor_position):
		"""save the given values temporarily and select the next entry"""
		self.stash(text, cursor_position)

		if self.index >= self._get_last_index():
			return False
		else:
			self.index += 1
			return True

	# ---------- getter ----------

	def is_committed(self, entry=None):
		if entry is None:
			entry = self.data[self.index]

		return entry[self.KEY_IS_COMMITTED]

	def get_text(self, entry=None):
		if entry is None:
			entry = self.data[self.index]

		return entry[self.KEY_TEXT]

	def get_cursor_position(self, entry=None):
		if entry is None:
			entry = self.data[self.index]

		return entry[self.KEY_CURSOR_POSITION]

	def is_newest(self):
		return self.index == len(self.data) - 1

	def is_oldest(self):
		return self.index == 0

	# ---------- internal ----------

	def stash(self, text, cursor_position):
		if text == self.get_text():
			self.data[self.index][self.KEY_CURSOR_POSITION] = cursor_position
			return

		stash = [False, text, cursor_position]
		if self.is_committed():
			self.index += 1
			self.data.insert(self.index, stash)
		else:
			self.data[self.index] = stash

	def _get_last_index(self):
		return len(self.data) - 1

	# ---------- debug code ----------

	def format(self):
		table = []
		table.append(("", "committed?", "value", "cursor"))
		for i in range(len(self.data)):
			ln = []
			if i == self.index:
				ln.append("> ")
			else:
				ln.append("")

			ln.extend(str(v) for v in self.data[i])
			table.append(ln)

		col_widths = [len(max((table[row][col] for row in range(len(table))), key=len)) for col in range(len(table[0]))]

		out = []
		for row in table:
			ln = "| "
			for cell, width in zip(row, col_widths):
				ln += cell.ljust(width)
				ln += " | "
			out.append(ln)

		hline = "-" * (sum(col_widths) + (len(col_widths)-1)*3 + 4)

		out.insert(0, hline)
		out.insert(2, hline)
		out.append( hline)

		return "\n".join(out)
