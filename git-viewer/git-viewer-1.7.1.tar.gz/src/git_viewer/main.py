#!/usr/bin/env python3

# Copyright © 2022 erzo <erzo@posteo.de>
# This work is free. You can use, copy, modify, and/or distribute it
# under the terms of the BSD Zero Clause License, see LICENSE.

"""\
Usage: gitl [<log-options>] [<revision-range>] [[--] <path>...] [-d <details-options>]

This is a keyboard driven git log viewer, similar to gitk but running in a terminal.
Call it from the git repository of which you want to see the history.

This help explains the command line arguments of gitl.
For a help how to use gitl open the program (without --help) and
press F1 or x (assuming you have not remapped those keys).

This program takes the following command line arguments:

    -d, --diff-options
                    all following command line arguments not listed below are
                    passed to the git commands used to display committed changes,
                    staged changes, unstaged changes and stashed changes.
                    All preceding command line arguments not listed below are
                    passed to the `git log` command used for the log view.
    --unreachable   show unreachable commits like dropped stashes.
                    All following command line arguments until -d not listed below
                    are passed to the `git fsck` command which is used to find the
                    unreachable commits
    --no-graph      don't pass --graph to git log
{doc_common_options}

All other command line arguments are passed through to git.
See the explanation of --diff-options.

Examples:

- show only commits touching a certain file:
      $ gitl main.py
- show a different branch:
      $ gitl origin/master
- search for a certain keyword in commit messages:
      $ gitl --grep bugfix
- search for a changed line:
      $ gitl -G "return None"
- search for changes on a specific (range of) line(s):
      $ gitl -L '144,+1:main.py'
- show a list of all tags:
      $ gitl --no-walk --tags
- show the reflog:
      $ gitl -g

- show more context lines:
      $ gitl -d -U6

For more information see
      $ git log --help
      $ git diff --help
      $ git help revisions
      $ git help cli
"""

doc_common_options = """
    --config FILE   a config file to load instead of the default config file
                    if you want to load this additionally to the default config file
                    start the file with `config.load --default`
    --command-pipe FILE
                    a named pipe which another program can write
                    commands to which gits will execute.
                    Create the pipe with `mkfifo FILE`.
                    The pipe is deleted by gits when gits quits
                    so that the controller can check if gits is still running.
    --open-always   open an urwid screen even if the view is empty
                    or if the start up checks do not pass, e.g. if
                    the current working directory is not a git repository.
                    This is useful if you want to run this in a separate terminal
                    window which closes immediately when this program quits.
    --git-dir PATH  the git directory which contains all git internal information
                    like objects, branches, tags etc
    --work-tree PATH the root directory of your project, this is usually the directory
                    in which the --git-dir is located but can be somewhere different
                    if you are using a bare repository, for an example see
                    https://wiki.archlinux.org/title/Dotfiles#Tracking_dotfiles_directly_with_Git
    --version       show the version of this progam as well as
                    the used python, urwid and git versions
    -h, --help      show this help
"""

import os
import stat
import re
import gettext
_ = gettext.gettext

import urwid

from . import color_decoder
from . import urwid_constants
from . import urwid_color_encoder
from . import urwid_edit_with_history
from . import urwid_text_layout
LogTextLayout = urwid_text_layout.LogTextLayout

from . import check
from . import model
from . import model_hints
from . import model_input_history
from . import api_commands
from . import api_subprocess
from . import settings
from . import utils
AlignedLine = api_commands.Command.AlignedLine
like_in = utils.like_in
Mnemonic = utils.Mnemonic

CANCEL = "cancel"
ACTIVATE = urwid.ACTIVATE
CURSOR_LEFT = urwid.CURSOR_LEFT
CURSOR_RIGHT = urwid.CURSOR_RIGHT
CURSOR_MAX_LEFT = urwid.CURSOR_MAX_LEFT
CURSOR_MAX_RIGHT = urwid.CURSOR_MAX_RIGHT
CURSOR_UP = urwid.CURSOR_UP
CURSOR_DOWN = urwid.CURSOR_DOWN
CURSOR_PAGE_UP = urwid.CURSOR_PAGE_UP
CURSOR_PAGE_DOWN = urwid.CURSOR_PAGE_DOWN
NEXT_SELECTABLE = 'next selectable'
PREV_SELECTABLE = 'prev selectable'
RESIZE = "window resize"

urwid.command_map['h'] = CURSOR_LEFT
urwid.command_map['j'] = CURSOR_DOWN
urwid.command_map['k'] = CURSOR_UP
urwid.command_map['l'] = CURSOR_RIGHT
urwid.command_map['esc'] = CANCEL


def measure_text_size(text_widget, max_width):
	"""
	Calculate the size of a Text widget.
	Text.pack is similar but ignores indentation, see urwid.text_layout.line_width.
	"""
	layout_struct = text_widget.base_widget.get_line_translation(max_width)
	height = len(layout_struct)
	width = max(sum(seg[0] for seg in ln) for ln in layout_struct)
	return width, height


def iter_commandmap_values(command_map):
	return command_map._command.values()

def iter_commandmap_keys(command_map):
	return command_map._command.keys()

def iter_commandmap_items(command_map):
	return command_map._command.items()

def clear_commandmap(command_map):
	return command_map._command.clear()


class MyListbox(urwid.ListBox):

	# is set in App.__init__
	app = None

	def iter_lines(self, reverse=False, *, notify_when_end_reached=True):
		start = self.focus_position

		if not reverse:
			start += 1
			for i in range(start, len(self.body)):
				yield i
			if notify_when_end_reached:
				self.app.show_warning(_("end reached, starting at top"))
			for i in range(0, start):
				yield i

		else:
			start -= 1
			for i in range(start, -1, -1):
				yield i
			if notify_when_end_reached:
				self.app.show_warning(_("top reached, starting at bottom"))
			for i in range(len(self.body)-1, start-1, -1):
				yield i

	def focus_first_line(self):
		self.set_focus(0)

	def focus_last_line(self):
		i = len(self.body) - 1
		self.set_focus(i)

	def focus_next_section(self):
		self.app.show_error(_("select next section is not implemented in this view"))

	def focus_prev_section(self):
		self.app.show_error(_("select previous section is not implemented in this view"))


	def keypress(self, size, key):
		out = super().keypress(size, key)
		if not out:
			self.app.auto_open()
		return out

	def set_focus(self, position, coming_from=None):
		super().set_focus(position, coming_from)
		self.app.auto_open()


class SelectableListbox(MyListbox):

	def __init__(self, *l, **kw):
		super().__init__(*l, **kw)
		# this is called again in reload
		if not hasattr(self, 'selection_history'):
			self.searching = False
			self.selection_history = model_input_history.History()

	# ------- details -------

	def has_details(self):
		return False

	def create_details_view(self):
		raise NotImplementedError()

	# ------- events -------

	def keypress(self, size, key):
		self.last_size = size
		if not super().keypress(size, key):
			return

		cmd = self._command_map[key]

		if cmd == CANCEL:
			if self.children_selectable():
				self.disable_selection()
				self.update_selected_child()
				self.app.show_clear()
				return

		return key

	# ------- search -------

	def search(self, search, reverse, *, notify_when_end_reached=True, enable_selection=True):
		for i in self.iter_lines(reverse, notify_when_end_reached=notify_when_end_reached):
			line_widget = self.body[i].base_widget
			if not hasattr(line_widget, "text"):
				continue

			if search(line_widget):
				if enable_selection:
					self.enable_selection()
				self.set_focus(i)
				return True

		return False

	# ------- selection -------

	def disable_selection(self):
		self.searching = False
		self.update_selected_child()
		self.save_focus(App.SAVE_BEFORE_LEAVE_VISUAL)

	def enable_selection(self):
		self.searching = True
		self.update_selected_child()
	
	def toggle_selection(self):
		if self.children_selectable():
			self.disable_selection()
		else:
			self.enable_selection()

	def children_selectable(self):
		return self.searching

	def update_selected_child(self):
		i = self.focus_position
		self.body[i].base_widget._invalidate()

	# ------- select first/last -------

	def focus_first_line(self):
		if self.children_selectable():
			for i in range(len(self.body)):
				widget = self.body[i].base_widget
				if widget.selectable():
					self.set_focus(i)
					return

		super().focus_first_line()

	def focus_last_line(self):
		if self.children_selectable():
			for i in range(len(self.body)-1, -1, -1):
				widget = self.body[i].base_widget
				if widget.selectable():
					self.set_focus(i)
					return

		super().focus_last_line()

	# ------- save selection -------

	def save_focus(self, occasion, *, commit=False):
		line_id = self.get_line_id()
		last_occasion = self.selection_history.get_cursor_position()
		if commit or last_occasion != occasion:
			self.selection_history.commit(line_id, occasion)
		else:
			self.selection_history.stash_and_next(line_id, occasion)

	def focus_prev(self):
		self.__focus(self.selection_history.stash_and_prev, error=_("there is no previous selection"))

	def focus_next(self):
		self.__focus(self.selection_history.stash_and_next, error=_("this is the newest selection"))

	def __focus(self, move_in_history, error):
		line_id = self.get_line_id()
		occasion = None
		if self.selection_history.is_newest():
			self.selection_history.commit(line_id, occasion)
		if not move_in_history(line_id, occasion):
			self.app.show_error(error)
			return
		self.load_current_focus()

	def get_line_id(self):
		return self.focus_position

	def load_current_focus(self):
		line_number = self.selection_history.get_text()
		n = len(self.body)
		if line_number >= n:
			line_number = n - 1
		self.set_focus(line_number)

	# ------- reload -------

	# this is just an internal function which can be used to implement `reload`
	# because reload does not make sense in help
	def do_reload(self):
		# save_focus is called by App
		offset = self.get_focus_offset_inset(self.last_size)[0]
		self.init_body()
		self.load_current_focus()
		# the documentation for urwid 1.3.1 mentions the following but unfortunately it's not implemented in urwid 2.1.2
		#self.set_focus_valign(('fixed top', offset))
		if offset == 0:
			self.set_focus_valign('top')
		elif offset == self.last_size[1] - 1:
			self.set_focus_valign('bottom')

class LineView(urwid.Text):

	def keypress(self, size, key):
		return key

	def get_markup(self):
		text, attributes = self.get_text()
		markup = list()
		i = 0
		for a,n in attributes:
			i1 = i + n
			markup.append((a, text[i:i1]))
			i = i1

		rest = text[i:]
		if rest:
			markup.append((None, rest))

		if not markup:
			markup.append((None, ""))

		return markup

class Hintable:

	HINTS_ALPHABET = "fdgjhksla"

	HINT_TYPE_HASH = "hash"
	HINT_TYPE_CMD = "cmd"
	attr_to_hint_type_map = {
		settings.COLOR_LINK : HINT_TYPE_HASH,
		settings.COLOR_CMD_IN_LINK : HINT_TYPE_CMD,
	}

	# ------- called by app -------

	def show_hints(self):
		visible = self.visible_line_widgets()
		markups = [widget.get_markup() for widget in visible]
		self.changed_widgets = visible
		self.original_markups = markups
		markups, num_links = self.mark_links(markups)
		assert isinstance(num_links, int), repr(num_links)
		key_gen = model_hints.generate_keys(self.HINTS_ALPHABET, num_links)
		links = dict()
		markups = self.add_hints(markups, key_gen, links)

		for line_widget, m in zip(visible, markups):
			line_widget.set_text(m)

		return links

	def remove_hints(self):
		for w, m in zip(self.changed_widgets, self.original_markups):
			w.set_text(m)

		self.changed_widgets = None
		self.original_markups = None

	# ------- internal methods -------

	def visible_line_widgets(self):
		"""the footer may hide widgets. so if you intend to call show_clear, do so before calling this method."""
		middle, top, bottom = self.calculate_visible(self.last_size)
		visible = []
		def append(widget):
			widget = widget.base_widget
			if isinstance(widget, LineView):
				visible.append(widget)
		for row in reversed(top[1]):
			append(row[0])
		append(middle[1])
		for row in bottom[1]:
			append(row[0])
		return visible

	def mark_links(self, markups):
		out = list()
		s = 0
		for m in markups:
			m, n = self.mark_links_one_line(m)
			out.append(m)
			s += n

		return out, s

	def mark_links_one_line(self, markup):
		raise NotImplementedError()

	def add_hints(self, markups, key_gen, out_links):
		out = list()
		for m in markups:
			m = self.add_hints_one_line(m, key_gen, out_links)
			out.append(m)

		return out

	hint_pattern = " [{key}] "
	def add_hints_one_line(self, markup, key_gen, out_links):
		out = []
		for attr, text in markup:
			out.append((attr, text))
			if attr in self.attr_to_hint_type_map:
				hint_type = self.attr_to_hint_type_map[attr]
				key = next(key_gen)
				hint = self.hint_pattern.format(key=key)
				hint = utils.colored_str_to_markup(hint, self.app.define_color)
				out.append((App.ATTR_HINT, hint))
				out_links[key] = (hint_type, text)

		if not out:
			out.append("")

		return out


# =============== Log View ===============

class LogEntryWidget(urwid.Text):

	def __init__(self, ln, hash_id, id_type, visual_mode):
		super().__init__(ln, wrap=urwid_text_layout.WRAP, align=urwid_text_layout.ALIGN)

		self.id_type = id_type
		self.hash_id = hash_id
		self.visual_mode = visual_mode

	def keypress(self, size, key):
		return key

	def selectable(self):
		return self.hash_id is not None and self.visual_mode()


class LogView(SelectableListbox):

	default_focus_lines = (settings.LOG_FOCUS_UNSTAGED, settings.LOG_FOCUS_STAGED, settings.LOG_FOCUS_LATEST_COMMIT)

	def __init__(self, log_model):
		self.model = log_model
		self.decoder = color_decoder.ColorDecoder()
		self.init_body()

		self.focus_default()
		self.enable_selection()

	def init_body(self):
		if urwid_text_layout.ALIGN != LogTextLayout.ALIGN_INDENTATION:
			self.model.remove_align_character()
		else:
			self.model.restore_align_character()

		self._index_untracked = None
		self._index_unstaged = None
		self._index_staged = None
		self._index_latest_commit = None
		widgets = [self.create_line_widget(i, *ln_tuple) for i, ln_tuple in enumerate(self.model.get_lines())]
		if not widgets:
			self.is_empty = True
			widgets.append(self.create_line_widget(0, _("log is empty"), None, model.TYPE_ERROR))
		else:
			self.is_empty = False
		body = urwid.SimpleFocusListWalker(widgets)
		super().__init__(body)

	def reload(self):
		self.do_reload()

	def create_line_widget(self, i, ln, hash_id, id_type):
		if hash_id == model.ID_UNTRACKED:
			self._index_untracked = i
		elif hash_id == model.ID_UNSTAGED:
			self._index_unstaged = i
		elif hash_id == model.ID_STAGED:
			self._index_staged = i
		elif id_type == model.TYPE_STASHED:
			pass
		elif hash_id is not None:
			if self._index_latest_commit is None:
				self._index_latest_commit = i

		if isinstance(ln, str):
			ln = ln.replace("\t", DetailsView.TAB)
			ln = self.decoder.decode(ln)

		if not ln:
			ln = ""

		widget = LogEntryWidget(ln, hash_id=hash_id, id_type=id_type, visual_mode=self.children_selectable)
		widget = DetailsAttrMap(widget)
		return widget

	def get_current_hash_id(self):
		selected_log_entry, position = self.body.get_focus()

		if selected_log_entry is None:
			return None, None

		w = selected_log_entry.base_widget
		return w.hash_id, w.id_type

	def has_details(self):
		return True

	def create_details_view(self):
		hash_id, id_type = self.get_current_hash_id()
		if hash_id is None:
			return None

		if hash_id == model.ID_STASHES_GROUP:
			view = LogView(model.StashesModel())
			view.hash_id = hash_id
		else:
			view = DetailsView(model.DetailsModel(hash_id, id_type))

		return view

	def is_correct_details_view(self, other):
		hash_id, id_type = self.get_current_hash_id()
		if hash_id == model.ID_STASHES_GROUP:
			return isinstance(other, LogView) and isinstance(other.model, model.StashesModel)

		if not isinstance(other, DetailsView):
			return False

		return other.hash_id == hash_id

	# ------- set focus -------

	def focus_first_line(self):
		super().focus_first_line()
		return True

	def focus_untracked(self):
		i = self._index_untracked

		if i is None and not model.LogModel.untracked_files_as_separate_group:
			i = self._index_unstaged

		if i is None:
			return False

		self.set_focus(i)
		return True

	def focus_unstaged(self):
		i = self._index_unstaged

		if i is None:
			return False

		self.set_focus(i)
		return True

	def focus_staged(self):
		i = self._index_staged

		if i is None:
			return False

		self.set_focus(i)
		return True

	def focus_latest_commit(self):
		i = self._index_latest_commit

		if i is None:
			return False

		self.set_focus(i)
		return True

	_focus_func_map = {
	}

	def focus_default(self):
		for key in self.default_focus_lines:
			if self._focus_by_key(key):
				return True
		return False
	
	def _focus_by_key(self, key):
		if key == settings.LOG_FOCUS_FIRST_LINE:
			return self.focus_first_line()
		elif key == settings.LOG_FOCUS_UNTRACKED:
			return self.focus_untracked()
		elif key == settings.LOG_FOCUS_UNSTAGED:
			return self.focus_unstaged()
		elif key == settings.LOG_FOCUS_STAGED:
			return self.focus_staged()
		elif key == settings.LOG_FOCUS_LATEST_COMMIT:
			return self.focus_latest_commit()
		else:
			self.app.show_error(_("INTERNAL ERROR: focus function %r unknown") % key)
			return False


	# ------- save selection -------

	def get_line_id(self):
		return self.get_current_hash_id()

	def load_current_focus(self):
		line_id = self.selection_history.get_text()
		hash_id, id_type = line_id
		search_cmp = lambda log_entry_widget: hash_id == log_entry_widget.hash_id and id_type == log_entry_widget.id_type
		found = self.search(search_cmp, reverse=False, notify_when_end_reached=False, enable_selection=False)
		if not found:
			self.app.show_warning(_('Failed to find line %s in log view.') % (line_id,))
			if id_type == model.TYPE_OTHER:
				if hash_id == model.ID_UNTRACKED:
					self.focus_unstaged() or self.focus_staged() or self.focus_latest_commit()
					return
				if hash_id == model.ID_UNSTAGED:
					self.focus_untracked() or self.focus_staged() or self.focus_latest_commit()
					return
				if hash_id == model.ID_STAGED:
					self.focus_unstaged() or self.focus_untracked() or self.focus_latest_commit()
					return
				if hash_id == model.ID_STASHES_GROUP:
					self.focus_first_line()
					return
			elif id_type == model.TYPE_STASHED:
				self.focus_first_line()
				return

			self.focus_latest_commit()


# =============== Details View ===============

class DetailsLineView(LineView):

	layout_no_auto_move_align_character = None

	def __init__(self, *l, **kw):
		auto_move_align_character = kw.pop('auto_move_align_character', True)
		self.file_info = kw.pop('file_info', None)
		self.line_info = kw.pop('line_info', None)
		self.ln = kw.pop('ln', None)
		self.ln_type = kw.pop('ln_type', None)
		super().__init__(*l,**kw)
		if not auto_move_align_character:
			self.layout = self.layout_no_auto_move_align_character


class DetailsErrorView(DetailsLineView):

	layout = LogTextLayout(align_character="^", repeat_prefix=True)
	prefix = _('\n    ! ^ERROR: ')
	suffix = _('\n')

	def __init__(self, text, **kw):
		text = [(App.ATTR_ERROR, self.prefix), (App.ATTR_WARNING, text+self.suffix)]
		kw['align'] = LogTextLayout.ALIGN_INDENTATION
		super().__init__(text, **kw)


class EllipsisWidget(DetailsLineView):

	def __init__(self, number_skipped_lines):
		text = _("[%s lines skipped]") % number_skipped_lines
		text = "\n %s%s\n" % (DetailsView.TAB, text)
		markup = (App.ATTR_ELLIPSIS, text)
		super().__init__(markup)


class DetailsAttrMap(urwid.AttrMap):

	@classmethod
	def init(cls, focus_map):
		cls.__focusmap_enabled = focus_map
		cls.__focusmap_disabled = None

	@property
	def _focus_map(self):
		if self.original_widget.selectable():
			return type(self).__focusmap_enabled
		else:
			return type(self).__focusmap_disabled

	@_focus_map.setter
	def _focus_map(self, focus_map):
		# is called in constructor with None
		pass

	def __init__(self, widget):
		super().__init__(widget, None)


class MetaLineInfo(model.LineInfo):

	__slots__ = ('meta_counter')

	_counter = 0

	def __init__(self, line_info=None):
		self.linenumber_after = -1
		self.linenumber_before_right = -1
		self.linenumber_before_left = -1
		self.is_modified = False
		self.meta_counter = type(self)._counter
		type(self)._counter += 1
	
	def store(self, line_info):
		self.linenumber_after = line_info.linenumber_after
		self.linenumber_before_right = line_info.linenumber_before_right
		self.linenumber_before_left = line_info.linenumber_before_left
		self.reset()
		self.meta_counter = type(self)._counter

	@classmethod
	def reset(cls):
		cls._counter = 0

	def __repr__(self):
		return super().__repr__()[:-1] + ", meta_counter=%s)" % self.meta_counter

class DetailsView(SelectableListbox, Hintable):

	TAB = 4 * " "

	divider_widget = urwid.Divider("─")

	max_lines_per_file = 500
	max_lines_per_file_blob = 5000

	align = settings.VAL_APP
	wrap = settings.VAL_APP


	def __init__(self, details_model):
		self.hash_id = details_model.hash_id
		self.id_type = details_model.id_type
		self.details_model = details_model

		self.decoder = color_decoder.ColorDecoder()
		self.init_body()
	
	def init_body(self):
		if type(self).align == settings.VAL_APP:
			self.align = urwid_text_layout.ALIGN
		if type(self).wrap == settings.VAL_APP:
			self.wrap = urwid_text_layout.WRAP

		if self.align != LogTextLayout.ALIGN_INDENTATION:
			self.details_model.remove_align_character()
		else:
			self.details_model.restore_align_character()

		self.current_file_info = None
		self.last_line_info = None
		self.widgets = []
		self.lines_current_file = 0
		lines = self.details_model.get_lines()
		if self.details_model.object_type == model.OBJECT_TYPE_BLOB:
			self.max_lines_per_file = self.max_lines_per_file_blob
		for ln in lines:
			self.append_line_widget(ln)
		self.append_ellipsis_if_necessary()
		if not self.widgets:
			self.is_empty = True
			self.append_line_widget((_("no output"), model.TYPE_ERROR))
		else:
			self.is_empty = False
		body = urwid.SimpleFocusListWalker(self.widgets)
		super().__init__(body)
		self.update_line_numbers(self.details_model.linenumber)

	def reload(self):
		self.do_reload()

	def append_line_widget(self, ln):
		auto_move_align_character = True
		line_info = None
		if isinstance(ln, tuple):
			if ln[1] == model.TYPE_START_OF_FILE:
				ln, ln_type, file_info = ln
			elif ln[1] == model.TYPE_NUMBERED_LINE:
				ln, ln_type, auto_move_align_character, line_info = ln
			elif ln[1] == model.TYPE_UNTRACKED:
				ln, ln_type, file_info = ln
			elif len(ln) == 2:
				ln, ln_type = ln
			else:
				ln, ln_type, auto_move_align_character = ln
			if ln_type == model.TYPE_ERROR:
				widget = DetailsErrorView(ln, wrap=urwid.SPACE, align=urwid.LEFT)
				widget = DetailsAttrMap(widget)
				self.widgets.append(widget)
				return
		else:
			ln_type = None

		if ln_type == model.TYPE_START_OF_FILE:
			self.new_file(file_info)
			MetaLineInfo.reset()
		elif self.details_model.is_start_new_file(ln):
			file_info = self.details_model.file_info
			self.new_file(file_info)
			MetaLineInfo.reset()

		self.lines_current_file += 1
		if self.lines_current_file > self.max_lines_per_file:
			return

		# urwid can't leave handling of tabs to the terminal
		# otherwise it couldn't handle linebreaks appropriately.
		# Handling of tabs would belong in the TextLayout, though.
		# That, however, would require (sc, i0, b"    ") text segments
		# and those would break backward compatibility with urwid < 2.1.0.
		if not isinstance(ln, list):
			ln = ln.replace("\t", self.TAB)

		if ln_type == model.TYPE_NUMBERED_LINE:
			markup = ""
		elif isinstance(ln, list):
			markup = ln
		else:
			markup = self.decoder.decode(ln)
			if not markup:
				markup = ""

		if line_info is None:
			line_info = MetaLineInfo()
		elif isinstance(self.last_line_info, MetaLineInfo):
			self.last_line_info.store(line_info)
		self.last_line_info = line_info

		if ln_type != model.TYPE_UNTRACKED:
			file_info = self.current_file_info

		widget = DetailsLineView(markup, ln=ln, ln_type=ln_type, file_info=file_info, line_info=line_info,
			wrap=self.wrap, align=self.align, auto_move_align_character=auto_move_align_character)
		widget.selectable = self.children_selectable
		widget = DetailsAttrMap(widget)
		self.widgets.append(widget)

	def new_file(self, file_info):
		self.append_ellipsis_if_necessary()
		self.widgets.append(self.divider_widget)
		self.lines_current_file = 0
		self.current_file_info = file_info

	def append_ellipsis_if_necessary(self):
		if self.lines_current_file > self.max_lines_per_file:
			n = self.lines_current_file - self.max_lines_per_file
			widget = EllipsisWidget(n)
			widget.selectable = self.children_selectable
			widget = DetailsAttrMap(widget)
			self.widgets.append(widget)

	def update_line_numbers(self, fmt):
		if self.details_model.is_merge:
			fmt = fmt.replace('{old}', model.DetailsModel.linenumber_sep.join(('{oldleft}', '{oldright}')))
		else:
			# for a normal commit oldright and oldleft are the same
			fmt = fmt.replace('{old}', '{oldright}')

		for widget in self.body:
			widget = widget.base_widget
			if widget == self.divider_widget or widget.ln_type != model.TYPE_NUMBERED_LINE:
				continue

			assert widget.line_info is not None
			linenumber = fmt.format(
				new=widget.line_info.formatted_linenumber_after,
				oldright=widget.line_info.formatted_linenumber_before_right,
				oldleft=widget.line_info.formatted_linenumber_before_left
			)
			#linenumber = utils.colored_str_to_markup(linenumber, self.app.define_color)
			linenumber = (settings.COLOR_LINE_NUMBERS, linenumber)
			sep = utils.colored_str_to_markup(self.details_model.linenumber_suffix, self.app.define_color)
			ln = self.decoder.decode(widget.ln)
			ln = [linenumber, sep, ln]
			widget.set_text(ln)

	def get_current_hash_id(self):
		return self.hash_id, self.id_type

	def get_current_filename(self):
		widget = self.focus.base_widget
		if not hasattr(widget, 'file_info'):
			return None
		file_info = widget.file_info
		if file_info is None:
			return None
		return file_info.fn

	def get_current_object_id(self, which):
		file_info = self.focus.base_widget.file_info
		if which == self.app.OPEN_AFTER:
			object_id = file_info.object_id_after
		elif which == self.app.OPEN_BEFORE_RIGHT:
			object_id = file_info.object_id_before_right
		elif which == self.app.OPEN_BEFORE_LEFT:
			object_id = file_info.object_id_before_left
		else:
			raise ValueError('invalid value for which %r' % which)

		if object_id == '0000000':
			object_id = None

		return object_id

	def get_current_line_number(self, which):
		line_view = self.focus.base_widget
		if line_view.line_info is None:
			return 0
		if isinstance(line_view.line_info, MetaLineInfo):
			return 0

		if which == self.app.OPEN_AFTER:
			line_number = line_view.line_info.linenumber_after
		elif which == self.app.OPEN_BEFORE_RIGHT:
			line_number = line_view.line_info.linenumber_before_right
		elif which == self.app.OPEN_BEFORE_LEFT:
			line_number = line_view.line_info.linenumber_before_left
		elif which == self.app.OPEN_NOW:
			#TODO: can I do better than this?
			# yes, I can: git blame --reverse 18cc32bef42f58387df1c00ec4aa33100560b421 --porcelain -L 635,635 main.py
			# although that only gives the line number for HEAD, not for the file in the actual working tree
			line_number = line_view.line_info.linenumber_after
		else:
			raise ValueError('invalid value for which %r' % which)
		return line_number

	# ------- save selection -------

	def get_line_id(self):
		fn = self.get_current_filename()
		if fn is None:
			return super().get_line_id()
		ln = self.focus.base_widget.line_info
		return (fn, ln)

	def load_current_focus(self):
		line_id = self.selection_history.get_text()
		if not isinstance(line_id, tuple):
			super().load_current_focus()
			return

		fn, ln = line_id
		assert fn is not None
		search_cmp = lambda widget: widget.file_info is not None and fn == widget.file_info.fn and self.is_line_info_greater_or_equal(widget.line_info, ln)
		found = self.search(search_cmp, reverse=False, notify_when_end_reached=False, enable_selection=False)
		if not found:
			self.app.show_warning(_('Failed to find line %s in details view.') % (line_id,))
			# no need to call self.select_first_line() because after recreating all widgets the first line is selected by default
			self.focus_file(fn)

	@staticmethod
	def is_line_info_greater_or_equal(ln1, ln2):
		"""ln1 >= ln2"""
		if ln1.linenumber_after == ln2.linenumber_after \
			and ln1.linenumber_before_right == ln2.linenumber_before_right \
			and ln1.linenumber_before_left == ln2.linenumber_before_left:
			if isinstance(ln1, MetaLineInfo):
				if isinstance(ln2, MetaLineInfo):
					return ln1.meta_counter >= ln2.meta_counter
				return False
			return True

		return ln1.linenumber_after >= ln2.linenumber_after \
			and ln1.linenumber_before_right >= ln2.linenumber_before_right \
			and ln1.linenumber_before_left >= ln2.linenumber_before_left

	# ------- links -------

	def mark_links_one_line(self, markup):
		out = list()
		n = 0
		for a, text in markup:
			i = 0
			for m in model.DetailsModel.reo_hash_id.finditer(text):
				i1 = m.start()
				if i1 > i:
					out.append((a, text[i:i1]))
					i = i1
				i1 = m.end()
				out.append((App.ATTR_LINK, text[i:i1]))
				n += 1
				i = i1

			remaining_text = text[i:]
			if remaining_text:
				out.append((a, remaining_text))

		return out, n

	# ------- set focus -------

	def focus_next_file(self):
		start = self.focus_position
		for i in range(start, len(self.body)):
			widget = self.body[i]
			if widget is self.divider_widget:
				i += 1
				break

		self.enable_selection()
		self.set_focus(i)

	def focus_prev_file(self):
		start = self.focus_position
		if start <= 0:
			return
		start -= 2
		i = None
		for i in range(start, -1, -1):
			widget = self.body[i]
			if widget is self.divider_widget:
				i += 1
				break

		if i is None:
			return

		self.enable_selection()
		self.set_focus(i)

	def focus_file(self, fn):
		for i in range(len(self.body)):
			widget = self.body[i]
			if widget is self.divider_widget:
				continue
			widget = widget.base_widget
			if widget.file_info is None:
				continue
			if widget.file_info.fn == fn:
				self.set_focus(i)
				return True

		return False

	def focus_next_hunk(self):
		is_same_hunk = True
		for i in range(self.focus_position, len(self.body)):
			widget = self.body[i].base_widget
			is_modified_line = isinstance(widget, DetailsLineView) and widget.line_info is not None and widget.line_info.is_modified
			if not is_modified_line:
				is_same_hunk = False
			elif not is_same_hunk:
				self.enable_selection()
				self.set_focus(i)
				return

		self.enable_selection()
		self.set_focus(i)

	def focus_prev_hunk(self):
		was_last_modified_line = None
		for i in range(self.focus_position-1, -1, -1):
			widget = self.body[i].base_widget
			is_modified_line = isinstance(widget, DetailsLineView) and widget.line_info is not None and widget.line_info.is_modified
			if was_last_modified_line and not is_modified_line:
				self.enable_selection()
				self.set_focus(i+1)
				return

			was_last_modified_line = is_modified_line

		self.enable_selection()
		self.set_focus(0)

	focus_next_section = focus_next_file
	focus_prev_section = focus_prev_file

	focus_next_paragraph = focus_next_hunk
	focus_prev_paragraph = focus_prev_hunk


# =============== Error View ===============

class CheckError(Exception):

	def __init__(self, error_number, error_message):
		super().__init__(error_message)
		self.error_number = error_number

class ErrorView(SelectableListbox):

	def __init__(self, error):
		widgets = []
		widgets.append(urwid.Text((App.ATTR_ERROR, str(error))))
		super().__init__(widgets)
		self.is_empty = False


# =============== Main View ===============

class SearchEdit(urwid_edit_with_history.EditWithHistory):

	PROMPT = "/"
	PROMPT_REVERSE = "?"

	FLAG_SEP = "/"

	flags = {
		'c' : ('case_sensitive', True),
		'i' : ('case_sensitive', False),
		'e' : ('is_regex', True),
		'f' : ('is_regex', False),
	}

	def __init__(self, app):
		super().__init__(multiline=False)
		self.app = app

	def set_search_text(self, search_text, *, case_sensitive, is_regex):
		flags = ''
		for flag, meaning in self.flags.items():
			if meaning == ('case_sensitive', case_sensitive):
				flags += flag
			elif meaning == ('is_regex', is_regex):
				flags += flag

		self.set_edit_text(search_text + self.FLAG_SEP + flags)
		self.set_edit_pos(len(search_text))
		self.history.commit(self.edit_text, self.edit_pos)


	def clear(self):
		self.edit_text = ""
	
	def set_direction(self, reverse):
		if reverse:
			caption = self.PROMPT_REVERSE
		else:
			caption = self.PROMPT

		self.set_caption(caption)

	def keypress(self, size, key):
		if not super().keypress(size, key):
			return

		cmd = self._command_map[key]
		if cmd == urwid.ACTIVATE:
			try:
				text, flags = self.parse_input()
			except ParseException as err:
				self.app.show_error(err.msg)
				return
			self.app.search_do(text, **flags)
		elif cmd == CANCEL:
			self.app.search_cancel()
	
	def parse_input(self):
		text = self.edit_text

		if self.FLAG_SEP in text:
			text, flags = text.rsplit(self.FLAG_SEP, 1)
			flags = self.parse_flags(flags)
		else:
			flags = {}

		return text, flags

	def parse_flags(self, text):
		flags = {}

		for c in text:
			if c in self.flags:
				key, val = self.flags[c]
				flags[key] = val
			else:
				supported_flags = _(",").join(self.flags.keys())
				self.error(_("invalid flag {flag}; should be one of {supported_flags}").format(flag=c, supported_flags=supported_flags))

		return flags

	def error(self, msg):
		raise ParseException(msg)

class ParseException(ValueError):

	def __init__(self, msg):
		super().__init__(msg)
		self.msg = msg


class SelectCommitEdit(urwid_edit_with_history.EditWithHistory):

	PROMPT = '"'

	def __init__(self, app):
		super().__init__(caption=self.PROMPT, multiline=False)
		self.app = app

	def clear(self):
		self.edit_text = ""

	def keypress(self, size, key):
		if not super().keypress(size, key):
			return

		cmd = self._command_map[key]
		if cmd == urwid.ACTIVATE:
			text = self.edit_text
			#self.app.select_commit(text)
			self.app.commands.execute('select %s' % api_commands.shlex.quote(text))
		elif cmd == CANCEL:
			self.app.search_cancel()



class SubCommandMap:

	def __init__(self, d=None):
		if d is None:
			d = {}
		self._command = d

	def __getitem__(self, key):
		return self._command.get(key)

	def __setitem__(self, key, value):
		self._command[key] = value

	def __delitem__(self, key):
		del self._command[key]

	def __contains__(self, other):
		raise NotImplementedError()

	def __iter__(self):
		raise NotImplementedError()


class App():

	# ------- constants -------

	APP_NAME = 'git-viewer'
	CONFIG_FILE_NAME = 'config'

	COMMENT = '#'
	KEY_ALL = '*'

	CD = color_decoder.ColorDecoder
	COLOR = urwid_constants.COLOR
	EMPH = urwid_constants.EMPH
	FOCUSED = "_focused"

	ATTR_TITLE  = settings.COLOR_TITLE
	ATTR_SUBTITLE  = settings.COLOR_SUBTITLE
	ATTR_DECORATION_BRANCH_LOCAL = settings.COLOR_DECORATION_BRANCH_LOCAL
	ATTR_DECORATION_BRANCH_REMOTE = settings.COLOR_DECORATION_BRANCH_REMOTE
	ATTR_DECORATION_TAG = settings.COLOR_DECORATION_TAG
	ATTR_DECORATION_HEAD = settings.COLOR_DECORATION_HEAD
	ATTR_DECORATION_HEAD_BRANCH_SEP = settings.COLOR_DECORATION_HEAD_BRANCH_SEP

	ATTR_INFO  = settings.COLOR_INFO
	ATTR_WARNING = settings.COLOR_WARNING
	ATTR_ERROR = settings.COLOR_ERROR
	ATTR_SUCCESS = settings.COLOR_SUCCESS

	ATTR_HINT = settings.COLOR_HINT
	ATTR_LINK = settings.COLOR_LINK

	ATTR_ELLIPSIS = settings.COLOR_ELLIPSIS
	ATTR_SPECIAL_CHARACTER = settings.COLOR_SPECIAL_CHARACTER

	ATTR_KEY = settings.COLOR_KEY
	ATTR_CMD = settings.COLOR_CMD

	BACKEND_CURSES = settings.BACKEND_CURSES
	BACKEND_RAW = settings.BACKEND_RAW
	BACKEND_AUTO = settings.VAL_AUTO
	backend = BACKEND_AUTO

	SAVE_BEFORE_GO_RIGHT = 'open'
	SAVE_BEFORE_SELECT_COMMIT = 'select'
	SAVE_BEFORE_SELECT_TAG = 'tag'
	SAVE_BEFORE_SELECT_SECTION = 'section'
	SAVE_BEFORE_SELECT_PARAGRAPH = 'paragraph'
	SAVE_BEFORE_SEARCH = 'search'
	SAVE_BEFORE_MOVE_ONE = 'move one'
	SAVE_BEFORE_MOVE_MANY = 'move many'
	SAVE_BEFORE_RELOAD = 'reload'
	SAVE_BEFORE_LEAVE_VISUAL = 'leave-visual'

	STATE_BEFORE_INIT = 0
	STATE_AFTER_INIT = 1
	STATE_RUNNING = 2

	RAW_COMPATIBLE_TERMINALS = (
		# gnome-terminal (colors don't look nice with curses)
		# sakura (seems to work equally well with both backends)
		"xterm-256color",
		# termite (seems to work equally well with both backends)
		"xterm-termite",
	)
	# RAW_INCOMPATIBLE_TERMINALS:
		# kitty (does not clear screen at exit)
		#"xterm-kitty"

	handle_mouse = False

	primitive_commands = set(iter_commandmap_values(urwid.command_map))


	# ------- key bindings -------

	VIM = 'vim'
	SWAY = 'sway'
	RANGER = 'ranger'
	QUTEBROWSER = 'qutebrowser'

	command_map_yank = SubCommandMap()
	command_map_yank['y'] = 'yank id'  //Mnemonic('inspired by vim, ranger and qutebrowser')
	command_map_yank['h'] = 'yank hash'
	command_map_yank['H'] = 'yank short hash'
	command_map_yank['t'] = 'yank subject'
	command_map_yank['s'] = 'yank subject'
	command_map_yank['n'] = 'yank name'
	command_map_yank['m'] = 'yank email'
	command_map_yank['a'] = 'yank author'
	command_map_yank['c'] = 'yank committer'
	command_map_yank['d'] = 'yank date'
	command_map_yank['b'] = 'yank body'
	command_map_yank['B'] = 'yank contents'
	command_map_yank['T'] = 'yank type'
	command_map_yank['l'] = 'yank "- subject\n  commit id"'  //Mnemonic('yank list item')
	command_map_yank['r'] = 'yank "bugfix for type id"'  //Mnemonic('yank reference')
	command_map_yank['E'] = 'yank "export GIT_COMMITTER_NAME=\'committer name\' GIT_COMMITTER_EMAIL=\'committer email\' GIT_AUTHOR_NAME=\'author name\' GIT_AUTHOR_EMAIL=\'author email\'"'
	command_map_yank['D'] = 'yank "export GIT_COMMITTER_DATE=\'committer date\' GIT_AUTHOR_DATE=\'author date\'"'
	command_map_yank['F'] = SubCommandMap({key : '%s --follow %s' % (cmd[:4], cmd[5:]) for key, cmd in iter_commandmap_items(command_map_yank)})
	command_map_yank['p'] = 'yank --no-git cwd'  //Mnemonic('yank path')
	command_map_yank['x'] = 'yank --no-git ""'
	command_map_yank['/'] = 'yank --no-git last search term'
	command_map_yank['P'] = 'yank --no-git absolute path'
	command_map_yank['f'] = 'yank --follow id'

	command_map_select = SubCommandMap()
	command_map_select['g'] = 'select --first-line' //like_in(VIM, RANGER, QUTEBROWSER)
	command_map_select['t'] = 'select --next-tag'
	command_map_select['T'] = 'select --prev-tag'
	command_map_select['h'] = 'go log'  //Mnemonic("inspired by ranger's go home")

	command_map_square_open = SubCommandMap()
	command_map_square_open['['] = 'select --prev-section' //like_in(VIM)

	command_map_square_close = SubCommandMap()
	command_map_square_close[']'] = 'select --next-section' //like_in(VIM)

	command_map_ctrl_w = SubCommandMap()
	command_map_ctrl_w['ctrl w'] = 'go toggle' //like_in(VIM)

	command_map = urwid.command_map
	command_map['q']     = 'quit'  //like_in(RANGER)
	command_map['v']     = 'layout ver'  //like_in(SWAY)
	command_map['b']     = 'layout hor'  //like_in(SWAY) + Mnemonic('h is already assigned to `go left` and b is next to v')
	command_map['w']     = 'layout one'  //like_in(SWAY)
	command_map['e']     = 'layout split'  //like_in(SWAY)
	command_map['t']     = 'go tag --toggle --last'
	command_map['T']     = 'go tag --toggle --containing'
	command_map['L']     = 'go right'  //like_in(QUTEBROWSER, RANGER)
	command_map['H']     = 'go left'   //like_in(QUTEBROWSER, RANGER)
	command_map['ctrl w']= command_map_ctrl_w
	command_map['y']     = command_map_yank
	command_map['o']     = 'open --now'
	command_map['i']     = 'open --after' //like_in(RANGER)
	command_map['I']     = 'open --before'
	command_map['U']     = 'open --before-left'
	command_map['a']     = 'set --cycle details-view.max-lines-per-file=500,9999 details-view.max-lines-per-file.blob=5000,9999'  //Mnemonic('a like all lines')
	command_map['X']     = 'linenumber --toggle'
	command_map['f5']    = 'reload --all'
	command_map['r']     = 'config.load'  //like_in(SWAY)
	command_map['p']     = 'config.edit'  //Mnemonic('p like preferences')
	command_map['S']     = 'option --diff --toggle -- --ignore-space-change'
	command_map['A']     = 'option --diff --toggle -- --ignore-all-space'
	command_map['W']     = 'option --diff --toggle -- --word-diff=color'
	command_map['E']     = 'option --diff --toggle -- --submodule=log'
	command_map['C']     = 'option --diff --toggle -- -U6'
	command_map['D']     = 'option --log --toggle -- --date=iso'
	command_map['Y']     = 'option --log --toggle -- --branches'  //Mnemonic('Y looks like two branches splitting')

	command_map['/']     = 'search --open'  //like_in(VIM, RANGER, QUTEBROWSER)
	command_map['?']     = 'search --reverse --open'  //like_in(VIM, QUTEBROWSER)
	command_map['n']     = 'search --next'  //like_in(VIM, RANGER, QUTEBROWSER)
	command_map['N']     = 'search --prev'  //like_in(VIM, RANGER, QUTEBROWSER)
	command_map['m']     = 'search --edit'
	command_map['"']     = 'select'
	command_map['g']     = command_map_select
	command_map['G']     = 'select --last-line'  //like_in(VIM, RANGER, QUTEBROWSER)
	command_map['ctrl o']= 'select --prev-selection'  //like_in(VIM)
	command_map['ctrl i']= 'select --next-selection'  //Mnemonic('only for the sake of documentation, the terminal intercepts <ctrl i> to insert a <tab> (https://github.com/urwid/urwid/issues/140)')
	command_map['shift tab'] = command_map['ctrl o']  //Mnemonic('<ctrl i> = <tab> so it makes sense to define <shift tab> to be the same like <ctrl o>')
	command_map['tab']       = command_map['ctrl i']  //Mnemonic('make <ctrl i> work like in vim, the terminal intercepts <ctrl i> to insert a <tab> (https://github.com/urwid/urwid/issues/140)')
	command_map['[']     = command_map_square_open
	command_map[']']     = command_map_square_close
	command_map['{']     = 'select --prev-paragraph'  //like_in(VIM)
	command_map['}']     = 'select --next-paragraph'  //like_in(VIM)
	command_map['f']     = 'link'  //like_in(QUTEBROWSER)
	command_map['f1']    = 'help --intro'
	command_map['x']     = 'help --intro' //Mnemonic('x is between s and c')
	command_map['f2']    = 'help --shortcuts'
	command_map['s']     = 'help --shortcuts'
	command_map['f3']    = 'help --commands'
	command_map['c']     = 'help --commands'
	command_map['f4']    = 'help --settings'
	command_map['d']     = 'help --settings' //Mnemonic('d is close to s, c and x')
	command_map['V']     = 'visual --toggle'  //Mnemonic('inspired by vim')
	command_map['ctrl f5'] = 'set details-view.auto-open!'
	command_map['<0>']   = 'set details-view.auto-open!'  //Mnemonic('<ctrl space> is intercepted by the terminal to insert a null character')
	command_map['<']   = 'set details-view.indent-broken-code=false'
	command_map['>']   = 'set details-view.indent-broken-code=true'

	command_map['-']          = 'resize -10'
	command_map['+']          = 'resize +10'
	command_map['ctrl left']  = 'resize --move-border -10'
	command_map['ctrl right'] = 'resize --move-border +10'


	command_map_standard = command_map

	command_replacement = {}
	command_replacement[NEXT_SELECTABLE] = 'go toggle'
	command_replacement[PREV_SELECTABLE] = 'go toggle'

	command_fallback = SubCommandMap()
	command_fallback[CURSOR_LEFT] = 'go left'
	command_fallback[CURSOR_RIGHT] = 'go details'
	command_fallback[CURSOR_MAX_LEFT] = 'select --first-line'
	command_fallback[CURSOR_MAX_RIGHT] = 'select --last-line'
	command_fallback[ACTIVATE]     = 'go details --open-only'
	command_fallback[CANCEL]       = 'go log'


	# ------- settings -------

	search_case_sensitive = None  # True|False|None. None = auto
	search_is_regex = False

	is_auto_open_enabled = True
	is_auto_reload_config_enabled = True

	pattern_error_in_command = _("Error: ^{err}  [in `{cmd}`]")
	pattern_mnemonic = "  [{mnemonic}]"

	help_show_all_shortcuts = True

	@property
	def align(self):
		return urwid_text_layout.ALIGN

	@align.setter
	def align(self, value):
		urwid_text_layout.ALIGN = value

	@property
	def align_character(self):
		return model.ALIGN_CHAR

	@align_character.setter
	def align_character(self, value):
		model.ALIGN_CHAR = value

	@property
	def wrap(self):
		return urwid_text_layout.WRAP

	@wrap.setter
	def wrap(self, value):
		urwid_text_layout.WRAP = value

	@property
	def explicit_spaces(self):
		return LogTextLayout.EXPLICIT_SPACES

	@explicit_spaces.setter
	def explicit_spaces(self, value):
		setting_explicit_spaces = "%app.explicit-spaces%"
		if not check.is_urwid_new_enough_for_explicit_spaces(fallback=True, assumption=_("I am assuming urwid is new enough to enable %s. This can lead to unexpected crashes.") % setting_explicit_spaces):
			self.show_warning(_("urwid is too old to enable %s. I am ignoring this setting.") % setting_explicit_spaces)
			value = False
		LogTextLayout.EXPLICIT_SPACES = value

	show_focus_in_all_views = True


	_log_level = settings.LOG_LEVEL_ALL
	_loglevels = []
	@property
	def log_level(self):
		return self._log_level
	@log_level.setter
	def log_level(self, value):
		self._loglevels.clear()
		self._log_level = value


	palette = [
		(ATTR_TITLE,   COLOR.FG_YELLOW,  COLOR.BG_DEFAULT),
		(ATTR_SUBTITLE, COLOR.FG_BRIGHT_WHITE+EMPH.BOLD, COLOR.BG_DEFAULT),
		(ATTR_DECORATION_BRANCH_LOCAL, COLOR.FG_GREEN+EMPH.BOLD, COLOR.BG_DEFAULT),
		(ATTR_DECORATION_BRANCH_REMOTE, COLOR.FG_RED+EMPH.BOLD, COLOR.BG_DEFAULT),
		(ATTR_DECORATION_TAG, COLOR.FG_YELLOW+EMPH.BOLD, COLOR.BG_DEFAULT),
		(ATTR_DECORATION_HEAD, COLOR.FG_CYAN+EMPH.BOLD, COLOR.BG_DEFAULT),
		(ATTR_DECORATION_HEAD_BRANCH_SEP, COLOR.FG_CYAN+EMPH.BOLD, COLOR.BG_DEFAULT),
		(ATTR_INFO,    COLOR.FG_DEFAULT, COLOR.BG_DEFAULT),
		(ATTR_WARNING, COLOR.FG_YELLOW,  COLOR.BG_DEFAULT),
		(ATTR_ERROR,   COLOR.FG_RED,     COLOR.BG_DEFAULT),
		(ATTR_SUCCESS, COLOR.FG_GREEN,   COLOR.BG_DEFAULT),
		(ATTR_LINK,    COLOR.FG_BLUE,    COLOR.BG_DEFAULT),
		(ATTR_HINT,    COLOR.FG_WHITE,   COLOR.BG_BLUE),
		(ATTR_ELLIPSIS, COLOR.FG_CYAN,   COLOR.BG_DEFAULT),
		(ATTR_SPECIAL_CHARACTER, COLOR.FG_CYAN, COLOR.BG_DEFAULT),
		(ATTR_KEY,     COLOR.FG_RED,     COLOR.BG_DEFAULT),
		(ATTR_CMD,     COLOR.FG_BLUE,    COLOR.BG_DEFAULT),
		(settings.COLOR_KEY_PRESSED, COLOR.FG_DEFAULT, COLOR.BG_DEFAULT),
		(settings.COLOR_MNEMONIC, COLOR.FG_BRIGHT_BLACK, COLOR.BG_DEFAULT),
		(settings.COLOR_CMD_IN_TEXT, COLOR.FG_BLUE, COLOR.BG_DEFAULT),
		(settings.COLOR_KEY_IN_TEXT, COLOR.FG_RED, COLOR.BG_DEFAULT),
		(settings.COLOR_CMD_IN_LINK, COLOR.FG_BLUE, COLOR.BG_DEFAULT),
		(settings.COLOR_LOG_STAGED, COLOR.FG_GREEN, COLOR.BG_DEFAULT),
		(settings.COLOR_LOG_UNSTAGED, COLOR.FG_RED, COLOR.BG_DEFAULT),
		(settings.COLOR_LOG_UNTRACKED, COLOR.FG_RED, COLOR.BG_DEFAULT),
		(settings.COLOR_LOG_STASHES, COLOR.FG_CYAN, COLOR.BG_DEFAULT),
		(settings.COLOR_DETAILS_UNTRACKED, COLOR.FG_BLUE, COLOR.BG_DEFAULT),
		(settings.COLOR_LINE_NUMBERS, COLOR.FG_CYAN, COLOR.BG_DEFAULT),
	]
	curses_palette = [
		(settings.COLOR_MNEMONIC, COLOR.FG_DEFAULT, COLOR.BG_DEFAULT),
	]
	focus_map = {}

	def get_color(self, color):
		for palette_tuple in reversed(self.palette):
			if palette_tuple[0] == color:
				return utils.palette_tuple_to_color_str(palette_tuple)
		raise AttributeError("attribute %r not contained in palette" % color)

	def set_color(self, color, value, *, define_if_not_existing=False):
		palette_tuple = utils.color_str_to_palette_tuple(color, value)
		self.set_palette_tuple(palette_tuple, define_if_not_existing=define_if_not_existing)

	def set_palette_tuple(self, palette_tuple, *, define_if_not_existing=False):
		color = palette_tuple[0]
		self._set_color(color, palette_tuple, define_if_not_existing=define_if_not_existing)

		color_focus = color + urwid_color_encoder.Generator.FOCUS_SUFFIX
		if define_if_not_existing:
			self.focus_map[color] = color_focus

		palette_tuple_focus = list(palette_tuple)
		palette_tuple_focus[0] = color_focus
		fg = palette_tuple_focus[1]
		if urwid_constants.EMPH.STANDOUT in fg:
			fg = fg.replace(urwid_constants.EMPH.STANDOUT, "")
		else:
			fg += urwid_constants.EMPH.STANDOUT
		palette_tuple_focus[1] = fg
		# before init they don't exist yet
		self._set_color(color_focus, palette_tuple_focus, define_if_not_existing=True)

	def _set_color(self, color, palette_tuple, *, define_if_not_existing=False):
		if self.state != self.STATE_BEFORE_INIT:
			self.screen.register_palette_entry(*palette_tuple)

		for i in range(len(self.palette)-1, -1, -1):
			if self.palette[i][0] == color:
				self.palette[i] = palette_tuple
				break
		else:
			if define_if_not_existing:
				self.palette.append(palette_tuple)
			else:
				raise AttributeError("attribute %r not contained in palette" % color)

	reo_other_setting = re.compile(r'%(?P<key>[^%]+)%$')
	def define_color(self, color):
		error_prefix = _("invalid color markup: ")
		invalid_color = "yellow,bold,italics/red"
		m = self.reo_other_setting.match(color)
		if m:
			other_key = m.group('key')
			try:
				other_attr, other_allowed_values, other_helpstr = settings.get(other_key)
			except KeyError:
				self.show_error(error_prefix + _("no such setting {other_key}").format(other_key=other_key))
				self.set_color(color, invalid_color, define_if_not_existing=True)
				return color
			if other_allowed_values != settings.TYPE_COLOR:
				self.show_error(error_prefix + _("{other_key} is not a color").format(other_key=other_key))
				self.set_color(color, invalid_color, define_if_not_existing=True)
				return color
			return other_key

		try:
			self.set_color(color, color, define_if_not_existing=True)
		except ValueError as e:
			self.show_error(error_prefix + str(e))
			self.set_color(color, invalid_color, define_if_not_existing=True)
		return color


	# ------- make classes accessible for settings -------

	model = model
	SearchEdit = SearchEdit
	LogView = LogView
	DetailsView = DetailsView
	LogModel = model.LogModel
	DetailsModel = model.DetailsModel
	DiffModel = model.DiffModel
	TextLayout = LogTextLayout
	Hintable = Hintable


	# ------- make functions accessible for commands -------

	iter_commandmap_values = staticmethod(iter_commandmap_values)
	iter_commandmap_keys = staticmethod(iter_commandmap_keys)
	iter_commandmap_items = staticmethod(iter_commandmap_items)
	clear_commandmap = staticmethod(clear_commandmap)


	# ------- app.init -------

	def __init__(self, diff=None, show=None, show_unreachable=False, log_args=[], unreachable_args=[], diff_args=[], config_file=None, command_pipe=None, open_always=False):
		error = None
		if open_always:
			def on_error(error_number, error_message):
				raise CheckError(error_number, error_message)
			check.error = on_error
		try:
			check.run_all_checks()
		except CheckError as e:
			error = e

		self._config_file = config_file
		self.continue_running = False
		self.state = self.STATE_BEFORE_INIT
		self.messages = []
		self.app = self

		from . import commands
		self.commands = api_commands.CommandContainer(self)
		self.commands.load_commands_from_module(commands)
		self.load_config(ignore_missing_file=True)

		model.append_cmd_log(log_args)
		model.append_cmd_diff(diff_args)
		model.append_cmd_unreachable(unreachable_args)
		urwid.Text.layout = LogTextLayout(model.ALIGN_CHAR)
		DetailsLineView.layout_no_auto_move_align_character = urwid.Text.layout.copy(auto_move_align_character=False)

		DetailsAttrMap.init(self.focus_map)
		MyListbox.app = self
		OverlayChoiceBox.app = self
		FocusIndicatorView.app = self
		HelpLineView.app = self
		model.DetailsModel.app = self
		model.LogModel.app = self

		g = urwid_color_encoder.Generator()
		for a, fg, bg in tuple(self.palette):
			if a.endswith(g.FOCUS_SUFFIX):
				continue
			af = a + g.FOCUS_SUFFIX
			self.palette.append((af, fg+urwid_constants.EMPH.STANDOUT, bg))
			self.focus_map[a] = af
		self.palette.extend(g.palette())
		self.focus_map.update(g.focus_map())
		self.focus_map[None] = self.CD.combine_colors(self.CD.NORMAL, self.CD.FG_DEFAULT, self.CD.BG_DEFAULT) + g.FOCUS_SUFFIX

		for key, cmd in iter_commandmap_items(self.command_map):
			if cmd in self.command_replacement:
				self.command_map[key] = self.command_replacement[cmd]

		self.main_views = []
		self.view_mode = self.VIEW_MODE_ONE
		if error:
			self.preferred_view_mode = self.VIEW_MODE_ONE
			view = ErrorView(error)
		elif diff is not None:
			self.preferred_view_mode = self.VIEW_MODE_ONE
			view = DetailsView(model.DiffModel(diff))
		elif show is not None:
			self.preferred_view_mode = self.VIEW_MODE_ONE
			view = DetailsView(model.DetailsModel(show, model.TYPE_OTHER))
		elif show_unreachable:
			view = LogView(model.UnreachableModel())
		else:
			view = LogView(model.LogModel())
		if view.is_empty and not open_always:
			return
		self.main_views.append(view)
		self.main_views_index = 0
		self.footer = None #urwid.Text()
		self.frame_widget = urwid.Frame(self.main_views[self.main_views_index], footer=self.footer)
		self.pressed_keys = ""
		self.is_pressed_keys_overlay_open = False
		self.select_commit_edit = None
		self.search_edit = None
		self.search_cmp = None
		self.search_direction_reversed = False
		self.links = None
		self.continue_running = True
		self._run_external = None
		self._is_first_run = True
		self._has_view_been_initialized = False

		self.command_pipe = command_pipe

		self.init_search(log_args)

	def init_search(self, log_args):
		HYPHEN_G = '-G'
		HYPHEN_S = '-S'
		i = 0
		n = len(log_args)
		while i < n:
			arg = log_args[i]
			if arg.startswith(HYPHEN_G):
				if arg == HYPHEN_G and i + 1 < n:
					i += 1
					arg = log_args[i]
				else:
					arg = arg[len(HYPHEN_G):]
				self.search_start(arg, case_sensitive=True, is_regex=True)
			if arg.startswith(HYPHEN_S):
				if arg == HYPHEN_S and i + 1 < n:
					i += 1
					arg = log_args[i]
				else:
					arg = arg[len(HYPHEN_S):]
				self.search_start(arg, case_sensitive=True, is_regex=False)
			i += 1

	def init_after_screen_creation(self):
		self.state = self.STATE_AFTER_INIT
		self._is_first_run = False
		self.load_config(ignore_missing_file=True)
		if not self._has_view_been_initialized:
			self.auto_select_view_mode()

		self.show = self._running__show
		self.reload = self._running__reload
		for attr, msg, kw in self.messages:
			self.show(attr, msg, **kw)
		del self.messages

		self.state = self.STATE_RUNNING

		if self.command_pipe:
			self.watch_command_pipe()

	def append_view(self, view, open_only=False):
		index = self.main_views_index + 1
		del self.main_views[index:]
		if not (open_only and self.should_be_visible(index)):
			self.main_views_index = index
		self.main_views.append(view)
		self.update_frame_body()
		if self.main_views_index == index:
			self.auto_open()

	def reopen_view(self, index, open_only=False):
		if not (open_only and self.should_be_visible(index)):
			self.main_views_index = index
		self.update_frame_body()
		if self.main_views_index == index:
			self.auto_open()

	def should_be_visible(self, index):
		if self.view_mode == self.VIEW_MODE_ONE:
			return index == self.main_views_index

		prefered_focus_position = self.prefered_focus_position
		if prefered_focus_position < 0:
			prefered_focus_position += self.number_views
		i = index - self.main_views_index + prefered_focus_position
		if i < 0:
			return False
		if i >= self.number_views:
			return False
		return True

	view_none = urwid.Filler(urwid.Text(""))
	def update_frame_body(self):
		if self.view_mode == self.VIEW_MODE_ONE:
			self.frame_widget.body = self.main_views[self.main_views_index]
		else:
			self.frame_widget.body.contents, self.frame_widget.body.focus_position = self.get_view_contents()

	prefered_focus_position = -2
	def get_views(self):
		if self.prefered_focus_position >= self.number_views:
			prefered_focus_position = self.number_views - 1
		elif self.prefered_focus_position < -self.number_views:
			prefered_focus_position = -self.number_views
		else:
			prefered_focus_position = self.prefered_focus_position

		if prefered_focus_position < 0:
			i1 = self.main_views_index - prefered_focus_position
			i0 = i1 - self.number_views
		else:
			i0 = self.main_views_index - prefered_focus_position
			i1 = i0 + self.number_views

		if i0 < 0:
			i1 += -i0
			i0 = 0
		else:
			n = len(self.main_views)
			while i1 > n and i0 > 0:
				i1 -= 1
				i0 -= 1

		views = self.main_views[i0:i1]
		while len(views) < i1 - i0:
			views.append(self.view_none)
		views = [FocusIndicatorView(v) for v in views]

		assert i0 <= self.main_views_index < i1, "%s <= %s < %s" % (i0, self.main_views_index, i1)

		focus = self.main_views_index - i0
		return views, focus

	def get_views_with_sizes(self):
		views, focus = self.get_views()
		self.update_view_sizes()
		views = [('weight', size, v) for size, v in zip(self.view_sizes, views)]
		return views, focus

	def get_view_contents(self):
		views, focus = self.get_views()
		self.update_view_sizes()
		views = [(v, self.frame_widget.body.options('weight', size)) for size, v in zip(self.view_sizes, views)]
		return views, focus

	def update_view_sizes(self):
		n = len(self.view_sizes)
		if n < self.number_views:
			for i in range(self.number_views - n):
				self.view_sizes.append(self.view_sizes[-1])
		elif n > self.number_views:
			for i in range(n - self.number_views):
				del self.view_sizes[-1]
		else:
			return
		self.ensure_view_sizes_add_up_to_100()

	def ensure_view_sizes_add_up_to_100(self):
		f = 100 / sum(self.view_sizes)
		for i in range(self.number_views):
			self.view_sizes[i] *= f

	def change_view_size(self, size_increment):
		if self.view_mode == self.VIEW_MODE_ONE:
			self.show_error(_("changing the size of the view is only possible if there are several views"))
			return

		# adjust the size of the other views
		size_decrement = size_increment / (self.number_views-1)

		focused_index = self.frame_widget.body.focus_position
		for i in range(self.number_views):
			if i == focused_index:
				new_size = self.view_sizes[i] + size_increment
			else:
				new_size = self.view_sizes[i] - size_decrement
			if new_size < 0:
				new_size = 0
			elif new_size > 100:
				new_size = 100
			self.view_sizes[i] = new_size

		self.ensure_view_sizes_add_up_to_100()
		self.update_frame_body()

	def move_view_border(self, size_increment):
		if self.view_mode == self.VIEW_MODE_ONE:
			self.show_error(_("changing the size of the view is only possible if there are several views"))
			return

		# adjust the size of one neighboring view
		size_decrement = size_increment

		focused_index = self.frame_widget.body.focus_position
		if focused_index >= self.number_views - 1:
			# this is the right most view => move left border
			left_index = focused_index - 1
			assert left_index >= 0
		else:
			left_index = focused_index

		for i in range(left_index, left_index+2):
			if i == left_index:
				new_size = self.view_sizes[i] + size_increment
			else:
				new_size = self.view_sizes[i] - size_decrement
			if new_size < 0:
				new_size = 0
			elif new_size > 100:
				new_size = 100
			self.view_sizes[i] = new_size

		self.ensure_view_sizes_add_up_to_100()
		self.update_frame_body()

	def run(self):
		self.screen = self.create_screen()
		self.loop = urwid.MainLoop(self.frame_widget, self.palette,
			handle_mouse=self.handle_mouse,
			input_filter=self.input_filter,
			screen = self.screen,
			unhandled_input=self.unhandled_input)
		self.screen.start()
		if self._is_first_run: # no need to check auto_switch_view_mode_on_resize, urwid sends a resize event as necessary
			self.init_after_screen_creation()
		self.loop.run()
		self.continue_running = False

	def create_screen(self):
		backend = self.backend
		if backend == self.BACKEND_AUTO:
			backend = self.get_auto_backend()

		if backend == self.BACKEND_RAW:
			import urwid.raw_display
			return urwid.raw_display.Screen()
		elif backend == self.BACKEND_CURSES:
			import urwid.curses_display
			for palette_tuple in self.curses_palette:
				self.set_palette_tuple(palette_tuple)
			return urwid.curses_display.Screen()
		else:
			raise NotImplementedError()
	
	def get_auto_backend(self):
		term = os.environ.get('TERM', None)
		if term in self.RAW_COMPATIBLE_TERMINALS:
			return self.BACKEND_RAW
		else:
			return self.BACKEND_CURSES


	def input_filter(self, keys, raw):
		out = []
		for k in keys:
			k = self.keypress(k)
			if k:
				out.append(k)

		return out

	def keypress(self, k):
		if k == RESIZE:
			if self.auto_switch_view_mode_on_resize:
				self.auto_select_view_mode()
			return k
		elif self.links:
			self.hint_input(k)
			return
		elif self.command_map is not self.command_map_standard:
			self.unhandled_input(k)
			return

		cmd = self.command_map[k]
		if cmd in (CURSOR_UP, CURSOR_DOWN):
			view = self.main_views[self.main_views_index]
			view.save_focus(self.SAVE_BEFORE_MOVE_ONE)
		elif cmd in (CURSOR_PAGE_UP, CURSOR_PAGE_DOWN):
			view = self.main_views[self.main_views_index]
			view.save_focus(self.SAVE_BEFORE_MOVE_MANY)

		return k

	def unhandled_input(self, k):
		self.show_clear()
		self.hide_pressed_keys()
		cmd = self.command_map[k]
		if isinstance(cmd, SubCommandMap):
			self.append_key(k)
			self.command_map = cmd
			self.show_pressed_keys(self.command_map, self.pressed_keys)
		elif cmd in self.primitive_commands:
			self.reset_command_map()
			self.unhandled_command(cmd)
		elif cmd:
			self.reset_command_map()
			self.execute_command(cmd)
		elif isinstance(k, tuple):
			# mouse event
			self.reset_command_map()
		else:
			self.append_key(k)
			self.show_error(_("undefined keyboard sortcut: %s") % self.pressed_keys)
			self.reset_command_map()

	def unhandled_command(self, cmd):
		cmd = self.command_fallback[cmd]
		if not cmd:
			return
		self.execute_command(cmd)

	def execute_command(self, cmd):
		self.commands.execute(cmd, state=self.state)


	def hint_input(self, k):
		if self.command_map[k] == CANCEL:
			self.remove_hints()
			return

		self.pressed_keys += k
		hint_type, link = self.links.get(self.pressed_keys, (None, None))
		if link is None:
			for keys in self.links.keys():
				if keys.startswith(self.pressed_keys):
					break
			else:
				self.remove_hints()
				self.show_error(_("invalid link hint: %s") % self.pressed_keys)
				self.pressed_keys = ""
				return
			self.show_info(self.pressed_keys)
			return

		callback = self.links_callback
		self.remove_hints()
		self.pressed_keys = ""
		callback(hint_type, link)


	KEY_SEP = _("")

	def append_key(self, key):
		if self.pressed_keys:
			self.pressed_keys += self.KEY_SEP
		self.pressed_keys += self.format_key(key)

	#WARNING: if you change this, also change the doc string of the help command
	keys_map = {
		' ' : 'space',
		'<' : 'less',
		'>' : 'greater',
	}
	@classmethod
	def format_key(cls, key):
		key = cls.keys_map.get(key, key)

		if len(key) == 1 and key != '?':
			return key
		else:
			return "<%s>" % key

	@classmethod
	def format_keys(cls, keys):
		return "".join(cls.format_key(k) for k in keys)

	@classmethod
	def parse_key(cls, key):
		if not hasattr(cls, 'reo_parse_key'):
			cls.reo_parse_key = re.compile(r'<([^<>]+|<[^<>]+>)>|([^<>])')
		keys = [cls._reverse_map_key(k) for k in cls.reo_parse_key.split(key) if k]
		assert len(keys) >= 1
		return keys

	@classmethod
	def _reverse_map_key(cls, key):
		for k1, k2 in cls.keys_map.items():
			if k2 == key:
				return k1
		return key

	def bind_key(self, key, cmd, *, cmdmap=None):
		new = True
		keys = self.parse_key(key)
		if cmdmap is None:
			cmdmap = self.command_map_standard
		for i in range(len(keys)-1):
			key = keys[i]
			val = cmdmap[key]
			if isinstance(val, SubCommandMap):
				cmdmap = val
			else:
				if val:
					self.show_info(_("overwriting key mapping {oldkey} with {newkey}").format(oldkey=self.format_keys(keys[:i+1]), newkey=self.format_keys(keys)))
				new = False
				cmdmap[key] = SubCommandMap()
				cmdmap = cmdmap[key]

		key = keys[-1]
		val = cmdmap[key]
		if isinstance(val, SubCommandMap):
			n = len(tuple(HelpViewGenerator.iter_commands(val, self.command_fallback)))
			self.show_info(_("overwriting {n} key mapping(s) starting with {key}").format(n=n, key=self.format_keys(keys)))
		elif val:
			self.show_info(_("overwriting key mapping {key}").format(key=self.format_keys(keys)))
		elif new:
			self.show_info(_("defining new key mapping {key}").format(key=self.format_keys(keys)))

		cmdmap[key] = cmd

	def unbind_key(self, key, *, cmdmap=None):
		if cmdmap is None:
			cmdmap = self.command_map_standard
		if key == self.KEY_ALL:
			n = len(tuple(HelpViewGenerator.iter_commands(cmdmap, self.command_fallback)))
			self.show_info(_("removing all {n} key mappings").format(n=n))
			clear_commandmap(cmdmap)
			return

		keys = self.parse_key(key)
		for key in keys[:-1]:
			val = cmdmap[key]
			if isinstance(val, SubCommandMap):
				cmdmap = val
			else:
				self.show_error(_("{key} was not mapped").format(key=self.format_keys(keys)))
				return

		key = keys[-1]
		val = cmdmap[key]
		if val is None:
			self.show_error(_("{key} was not mapped").format(key=self.format_keys(keys)))
			return

		if isinstance(val, SubCommandMap):
			n = len(tuple(HelpViewGenerator.iter_commands(val, self.command_fallback)))
			self.show_info(_("removing all {n} key mappings starting with {key}").format(n=n, key=self.format_keys(keys)))
		else:
			self.show_info(_("unmapping {key}").format(key=self.format_keys(keys)))
		del cmdmap[key]

	def bind_fallback(self, cmd_primitive, cmd_programmable):
		if cmd_primitive in self.primitive_commands:
			old_cmd_programmable = self.command_fallback[cmd_primitive]
			if old_cmd_programmable:
				self.show_info(_("changing fallback command for `{cmd_primitive}`: `{cmd_fallback_old}` -> `{cmd_fallback_new}`")
					.format(cmd_primitive=cmd_primitive, cmd_fallback_old=old_cmd_programmable, cmd_fallback_new=cmd_programmable))
			else:
				self.show_info(_("defining new fallback command for `{cmd_primitive}`: `{cmd_fallback_new}`")
					.format(cmd_primitive=cmd_primitive, cmd_fallback_new=cmd_programmable))
			self.command_fallback[cmd_primitive] = cmd_programmable
		else:
			self.show_error(_("`{cmd}` is not a primitive command").format(cmd=cmd_primitive))

	def unbind_fallback(self, cmd_primitive):
		if cmd_primitive == self.KEY_ALL:
			n = len(tuple(iter_commandmap_keys(self.command_fallback)))
			self.show_info(_("removing all {n} fallback commands").format(n=n))
			clear_commandmap(self.command_fallback)
			return

		if self.command_fallback[cmd_primitive] is None:
			self.show_error(_("`{primitive}` did not have a fallback").format(primitive=cmd_primitive))
		else:
			self.show_info(_("removing fallback command from `{cmd}`").format(cmd=cmd_primitive))
			del self.command_fallback[cmd_primitive]

	def reset_command_map(self):
		self.pressed_keys = ""
		self.command_map = self.command_map_standard


	ID_STAGED = model.ID_STAGED
	ID_UNSTAGED = model.ID_UNSTAGED
	ID_UNTRACKED = model.ID_UNTRACKED
	ID_STASHES_GROUP = model.ID_STASHES_GROUP

	TYPE_STASHED = model.TYPE_STASHED
	TYPE_OTHER = model.TYPE_OTHER
	TYPE_ERROR = model.TYPE_ERROR
	TYPE_TAG = model.TYPE_TAG

	def get_current_hash_id(self):
		view = self.main_views[self.main_views_index]
		i = self.main_views_index
		while not hasattr(view, 'get_current_hash_id'):
			i -= 1
			if i < 0:
				return None, None
			view = self.main_views[i]
		return view.get_current_hash_id()

	def quit(self):
		raise urwid.ExitMainLoop()


	# ------- config -------

	paths = []

	def load_config(self, fn=None, default_path=False, ignore_missing_file=False, log_level=settings.LOG_LEVEL_WARNING):
		'''
		allowed in state 0:
			- show_error
			- show_warning
			- show_info
			- show_success
			- execute_command (commands.execute)
			- reload
		'''
		fn_bak = fn
		fn = self.parse_config_file_name(fn, only_existing=True, default_path=default_path)
		if not fn:
			if not ignore_missing_file and self.state != self.STATE_AFTER_INIT:
				fn = fn_bak if fn_bak else self.CONFIG_FILE_NAME
				self.show_error(_("config file not found: %s") % fn)
			return

		if not os.path.isfile(fn):
			if not ignore_missing_file and self.state != self.STATE_AFTER_INIT:
				self.show_error(_('%s is not a file') % fn)
			return

		if fn in self.paths:
			if self.state != self.STATE_AFTER_INIT:
				self.show_error(_("circular config.load: {to_be_loaded} is loaded in {current}").format(to_be_loaded=fn, current=self.paths[-1]))
			return

		self.paths.append(fn)

		self.save_and_set_log_level(log_level)
		with open(fn, 'rt') as f:
			for ln in f:
				self.execute_line(ln)
		self.restore_log_level_if_it_has_not_been_changed()

		if self.auto_switch_view_mode_on_resize and self.state == self.STATE_RUNNING:
			self.auto_select_view_mode()

		del self.paths[-1]

	def execute_line(self, ln):
		ln = ln.strip()
		if not ln:
			return
		if ln.startswith(self.COMMENT):
			return
		self.execute_command(ln)


	def export_config(self, fn, *, settings=True, keybindings=True, overwrite=False, default_path=False, ignore_settings={'app.log-level'}, comment_out=False, export_help=True):
		fn = self.parse_config_file_name(fn, prefer_existing=False, default_path=default_path)
		if not fn:
			self.show_error(_("no default path"))
			return

		if not overwrite and os.path.exists(fn):
			self.show_error(_('%s exists already') % fn)
			return

		with open(fn, 'wt') as f:
			def write(ln):
				if comment_out and ln:
					ln = self.COMMENT + ln
				ln = ln.replace('\n', r'\n')
				f.write(ln)
				f.write("\n")

			def write_heading(header):
				prefix = self.COMMENT
				rule = 80 * self.COMMENT
				write(prefix + rule)
				write(prefix + ' ' + header.title())
				write(prefix + rule)
				write('')

			if settings:
				write_heading(_("settings"))
				for ln in self.iter_setting_lines(ignore_settings=ignore_settings, export_help=export_help):
					write(ln)
				if keybindings:
					write("")

			if keybindings:
				write_heading(_("key mappings"))
				for ln in self.iter_keybinding_lines():
					write(ln)

		self.show_info(_("exported config to %s") % fn)

	def iter_setting_lines(self, *, ignore_settings=None, export_help=True):
		for key in settings.keys():
			if ignore_settings and key in ignore_settings:
				continue
			yield from self.format_export_setting_line(key, export_help=export_help)

	def format_export_setting_line(self, key, export_help=True):
		attr, allowed_values, help_str = settings.get(key)
		if export_help:
			prefix = self.COMMENT + ' '
			yield prefix + key
			yield prefix + '-'*len(key)
			yield prefix + "%s: %s" % (settings.label_allowed_values(allowed_values), settings.format_allowed_values(allowed_values))
			for ln in help_str.splitlines():
				yield prefix + ln
			if isinstance(allowed_values, (tuple, list)):
				if allowed_values[0] == list:
					allowed_values_to_iter = allowed_values[1]
				else:
					allowed_values_to_iter = allowed_values
				for valname, value, valhelp in settings.iter_allowed_values(allowed_values_to_iter):
					if valhelp:
						yield prefix + "%s: %s" % (valname, valhelp)

		value = settings.rgetattr(self, attr)
		value = settings.format_value(value, allowed_values)
		value = api_commands.quote(value)
		ln = "set {key}={value}".format(key=key, value=value)
		yield ln

		if export_help:
			yield ''

	def iter_keybinding_lines(self):
		yield "unmap %s" % self.KEY_ALL
		for key, cmds in HelpViewGenerator.iter_commands(self.command_map_standard, self.command_fallback):
			cmd = cmds[0]
			yield self.format_export_map_line(key, cmd)

		yield ""

		yield "unmap-fallback %s" % self.KEY_ALL
		for prim, prog in iter_commandmap_items(self.command_fallback):
			yield self.format_export_map_fallback_line(prim, prog)

	def format_export_map_line(self, key, cmd):
		key = api_commands.quote(key)
		cmd = api_commands.quote(cmd)
		ln = "map {key} {cmd}".format(key=key, cmd=cmd)
		return ln

	def format_export_map_fallback_line(self, primitive_cmd, programmable_cmd):
		primitive_cmd = api_commands.quote(primitive_cmd)
		programmable_cmd = api_commands.quote(programmable_cmd)
		ln = "map-fallback {primitive_cmd} {programmable_cmd}".format(primitive_cmd=primitive_cmd, programmable_cmd=programmable_cmd)
		return ln


	def open_config(self, fn, *, ignore_existing=True, default_path=False):
		err = model.check_editor()
		if err:
			self.show_error(err)
			return

		fn = self.parse_config_file_name(fn, prefer_existing=not ignore_existing, default_path=default_path)

		if not os.path.exists(fn):
			os.makedirs(os.path.split(fn)[0], exist_ok=True)
			self.export_config(fn, comment_out=True)

		def do():
			model.open_file_in_editor(fn, line_number=None, create_dirs=True)
			if self.is_auto_reload_config_enabled:
				self.load_config(fn)

		self._run_external = do
		self._reload_after_run_external = False
		raise urwid.ExitMainLoop()


	def get_app_dirs(self):
		if hasattr(self, '_appdirs'):
			return self._appdirs

		try:
			from platformdirs import PlatformDirs as AppDirs
		except:
			try:
				from xdgappdirs import AppDirs
			except:
				try:
					from appdirs import AppDirs
				except:
					return None
		self._appdirs = AppDirs(self.APP_NAME, multipath=True)
		return self._appdirs

	def get_config_paths(self):
		app_dirs = self.get_app_dirs()
		if app_dirs:
			yield from app_dirs.user_config_dir.split(os.pathsep)
			yield from app_dirs.site_config_dir.split(os.pathsep)
		else:
			path = os.environ.get('XDG_CONFIG_HOME', None)
			if not path:
				path = os.path.expanduser('~')
				path = os.path.join(path, '.config')
			path = os.path.join(path, self.APP_NAME)
			yield path

	def get_config_files(self, filename=None, *, only_existing=True):
		if not filename:
			filename = self.CONFIG_FILE_NAME

		for path in self.get_config_paths():
			fn = os.path.join(path, filename)
			if only_existing and not os.path.isfile(fn):
				continue
			yield fn

	def parse_config_file_name(self, fn=None, *, only_existing=False, prefer_existing=False, default_path=False):
		if not default_path:
			if not fn:
				fn = self._config_file
			if fn:
				fn = os.path.expanduser(fn)
				if self.paths and not os.path.isabs(fn):
					path = os.path.split(self.paths[-1])[0]
					fn = os.path.join(path, fn)
				return fn

		try:
			return next(self.get_config_files(fn, only_existing=only_existing or prefer_existing))
		except StopIteration:
			if prefer_existing and not only_existing:
				return next(self.get_config_files(fn, only_existing=False))

		return None


	# ------- command file -------
	# a command file has the same syntax like a config file but the following differences:
	# - it may be executed only after initialization is complete, inside of the urwid loop
	# - all programmable commands are allowed

	POLL_TIME_S = .2

	def watch_command_pipe(self):
		import threading
		import queue
		self.command_queue = queue.Queue()
		threading.Thread(target=self._read_command_pipe_thread).start()
		self.loop.set_alarm_in(self.POLL_TIME_S, self._poll_command_queue)

	def _read_command_pipe_thread(self):
		if not os.path.exists(self.command_pipe):
			self.command_queue.put(Exception(_("%r does not exist, please create it using mkfifo") % self.command_pipe))
			return
		if not stat.S_ISFIFO(os.stat(self.command_pipe).st_mode):
			self.command_queue.put(Exception(_("%r is not a named pipe, please create it using mkfifo") % self.command_pipe))
			return
		try:
			while self.command_pipe:
				with open(self.command_pipe, 'rt') as pipe:
					for ln in pipe:
						self.command_queue.put(ln)
		except OSError as e:
			self.command_queue.put(e)

	def _poll_command_queue(self, loop, args):
		while not self.command_queue.empty():
			ln = self.command_queue.get()
			if isinstance(ln, Exception):
				self.show_error(ln)
				return
			self.execute_line(ln)
		self.loop.set_alarm_in(self.POLL_TIME_S, self._poll_command_queue)

	def close_command_pipe(self):
		if self.command_pipe:
			path = self.command_pipe

			# stop read thread
			self.command_pipe = None
			with open(path, 'wt') as pipe:
				pipe.write("")

			os.remove(path)


	def exec_command_file(self, fn):
		with open(fn, 'rt') as f:
			for ln in f:
				self.execute_line(ln)


	# ------- hints -------

	HINT_TYPE_HASH = Hintable.HINT_TYPE_HASH
	HINT_TYPE_CMD = Hintable.HINT_TYPE_CMD

	def show_hints(self, callback):
		view = self.main_views[self.main_views_index]
		if not hasattr(view, 'show_hints'):
			self.show_error(_("links are not supported in this view"))
			return

		self.show_clear()
		self.links = view.show_hints()
		self.links_callback = callback

	def remove_hints(self):
		view = self.main_views[self.main_views_index]
		view.remove_hints()
		self.links = None
		self.links_callback = None
		self.show_clear()

	def follow_link(self, hint_type, value):
		if hint_type == self.HINT_TYPE_HASH:
			self.select_commit(value)
		elif hint_type == self.HINT_TYPE_CMD:
			self.show_help_for_command(value.strip('`'))
		else:
			raise NotImplementedError("unsupported hint_type %r" % hint_type)


	# ------- view modes -------

	VIEW_MODE_VER = "ver"
	VIEW_MODE_HOR = "hor"
	VIEW_MODE_ONE = "one"
	PSEUDO_VIEW_MODE_SPLIT = "split"
	PSEUDO_VIEW_MODE_AUTO = "auto"

	preferred_view_mode = VIEW_MODE_HOR
	number_views = 2
	min_width_for_hor  = number_views*100
	min_height_for_ver = number_views*35
	column_widths = [100/number_views] * number_views
	row_heights = list(column_widths)
	auto_switch_view_mode_on_resize = True

	def auto_select_view_mode(self):
		if self.preferred_view_mode == self.VIEW_MODE_ONE:
			self.view(self.VIEW_MODE_ONE)
			return

		width, height = self.screen.get_cols_rows()
		if self.preferred_view_mode == self.VIEW_MODE_HOR:
			if width >= self.min_width_for_hor:
				self.view(self.VIEW_MODE_HOR)
				return
			elif height >= self.min_height_for_ver:
				self.view(self.VIEW_MODE_VER)
				return
		else:
			if height >= self.min_height_for_ver:
				self.view(self.VIEW_MODE_VER)
				return
			elif width >= self.min_width_for_hor:
				self.view(self.VIEW_MODE_HOR)
				return

		self.view(self.VIEW_MODE_ONE)

	def view(self, mode, number_views=None):
		if mode == self.PSEUDO_VIEW_MODE_AUTO:
			self.auto_select_view_mode()
			return
		elif mode == self.PSEUDO_VIEW_MODE_SPLIT:
			if self.view_mode == self.VIEW_MODE_HOR:
				self.view(self.VIEW_MODE_VER, number_views)
				return
			else:
				self.view(self.VIEW_MODE_HOR, number_views)
				return

		self._has_view_been_initialized = True
		self.view_mode = mode
		if number_views:
			self.number_views = number_views

		if mode == self.VIEW_MODE_HOR:
			self.view_sizes = self.column_widths
			views, focus = self.get_views_with_sizes()
			self.frame_widget.body = NotifyingColumns(views, focus_column=focus, on_focus_change=self.update_main_views_index)
		elif mode == self.VIEW_MODE_VER:
			self.view_sizes = self.row_heights
			views, focus = self.get_views_with_sizes()
			self.frame_widget.body = NotifyingPile(views, focus_item=focus, on_focus_change=self.update_main_views_index)
		elif mode == self.VIEW_MODE_ONE:
			self.frame_widget.body = self.main_views[self.main_views_index]
		else:
			self.show_info(_("not implemented view mode %s") % mode)

		self.is_pressed_keys_overlay_open = False
		self.auto_open()

	def update_main_views_index(self):
		container = self.frame_widget.body
		focused_widget = container.focus.base_widget
		self.main_views_index = self.main_views.index(focused_widget)


	GO_LEFT = "left"
	GO_RIGHT = "right"
	GO_TOGGLE = "toggle"
	GO_LOG = "log"
	GO_DETAILS = "details"
	GO_TAG = "tag"

	def auto_open(self):
		if not self.is_auto_open_enabled:
			return

		if self.view_mode == self.VIEW_MODE_ONE:
			return

		self.go(self.GO_DETAILS, open_only=True, explicit=False)

	def go(self, direction, open_only=False, explicit=True):
		self.go_map[direction](self, open_only=open_only, explicit=explicit)

	def go_log(self, open_only=False, explicit=True):
		if self.main_views_index == 0:
			return

		self.reopen_view(0, open_only=open_only)

	def go_left(self, open_only=False, explicit=True):
		if self.main_views_index == 0:
			return

		self.reopen_view(self.main_views_index - 1, open_only=open_only)

	def go_right(self, open_only=False, explicit=True):
		if self.main_views_index + 1 >= len(self.main_views):
			return

		self.reopen_view(self.main_views_index + 1, open_only=open_only)

	def go_toggle(self, open_only=False, explicit=True):
		'''toggle between visible views'''
		if self.view_mode == self.VIEW_MODE_ONE:
			return

		container = self.frame_widget.body
		n = len(container.contents)
		i = container.focus_position
		if i + 1 < n:
			container.focus_position = i + 1
		else:
			container.focus_position = 0

		try:
			self.update_main_views_index()
		except:
			container.focus_position = i

	def go_details(self, open_only=False, explicit=True):
		view = self.main_views[self.main_views_index]
		if not view.children_selectable():
			return

		if explicit and hasattr(view, 'save_focus'):
			view.save_focus(self.SAVE_BEFORE_GO_RIGHT)
		if not view.has_details():
			if self.main_views_index + 1 < len(self.main_views):
				self.reopen_view(self.main_views_index + 1, open_only=open_only)
			return

		if self.main_views_index + 1 < len(self.main_views):
			next_view = self.main_views[self.main_views_index+1]
			if hasattr(view, 'is_correct_details_view') and view.is_correct_details_view(next_view):
				self.reopen_view(self.main_views_index + 1, open_only=open_only)
				return

		view = view.create_details_view()
		if view is None:
			return

		self.append_view(view, open_only=open_only)

	def go_tag(self, toggle=False, containing=False, open_only=False, explicit=True):
		hash_id, id_type = self.get_current_hash_id()

		if id_type == model.TYPE_TAG:
			current_tag = hash_id
			hash_id, id_type = self.main_views[self.main_views_index-1].get_current_hash_id()
		else:
			current_tag = None

		tag = self.get_closest_tag(hash_id, containing, exclusive=False)
		if tag is None:
			return

		if current_tag is not None:
			if tag == current_tag:
				if toggle:
					self.go_left()
				return

			self.main_views_index -= 1
		elif self.main_views_index + 1 < len(self.main_views):
			next_view = self.main_views[self.main_views_index+1]
			if isinstance(next_view, DetailsView):
				next_details_model = next_view.details_model
				if next_details_model.id_type == model.TYPE_TAG and next_details_model.hash_id == tag:
					self.reopen_view(self.main_views_index+1, open_only=open_only)
					return

		view = DetailsView(model.DetailsModel(tag, model.TYPE_TAG))
		self.append_view(view, open_only=open_only)

	def get_closest_tag(self, hash_id, containing, exclusive):
		if hash_id in model.SPECIAL_IDS:
			if containing:
				self.show_error(_("no containing tag for {hash_id}").format(hash_id=hash_id))
				return
			else:
				hash_id = "HEAD"

		if hash_id is None:
			self.show_error(_("no tag without a hash id"))
			return

		if containing:
			tag = model.get_containing_tag(hash_id, exclusive=exclusive)
			if tag is None:
				self.show_error(_("no containing tag"))
				return
		else:
			tag = model.get_last_tag(hash_id, exclusive=exclusive)
			if tag is None:
				self.show_error(_("no previous tag"))
				return

		return tag


	go_map = {
		GO_LEFT : go_left,
		GO_RIGHT : go_right,
		GO_TOGGLE : go_toggle,
		GO_LOG : go_log,
		GO_DETAILS : go_details,
		GO_TAG : go_tag,
	}


	def reload(self, only_current=True):
		pass

	def _running__reload(self, only_current=True):
		is_auto_open_enabled = self.is_auto_open_enabled
		self.is_auto_open_enabled = False

		model.DetailsModel.clear_cache()

		start = self.main_views_index
		if only_current:
			stop = start - 1
		else:
			stop = -1
		for i in range(start, stop, -1):
			view = self.main_views[i]
			if hasattr(view, 'save_focus'):
				view.save_focus(self.SAVE_BEFORE_RELOAD)
			if hasattr(view, 'reload'):
				view.reload()

		self.is_auto_open_enabled = is_auto_open_enabled

		del self.main_views[self.main_views_index+1:]
		self.auto_open()


	# ------- move cursor to commit -------

	def select_commit_open_edit(self, clear=True):
		if self.select_commit_edit is None:
			self.select_commit_edit = SelectCommitEdit(self)

		if clear:
			self.select_commit_edit.clear()

		self.frame_widget.footer = self.select_commit_edit
		self.frame_widget.focus_position = "footer"

	def select_commit(self, search_text, save_focus=True):
		view = self.main_views[self.main_views_index]
		if isinstance(view, LogView):
			if save_focus:
				view.save_focus(self.SAVE_BEFORE_SELECT_COMMIT, commit=True)
			search_cmp = lambda log_entry_widget: log_entry_widget.hash_id and search_text.startswith(log_entry_widget.hash_id)
			found = view.search(search_cmp, reverse=False, notify_when_end_reached=False)
		else:
			if search_text and search_text[0] == ':':
				hash_id, id_type = self.get_current_hash_id()
				search_text = hash_id + search_text

			try:
				view = DetailsView(model.DetailsModel(search_text, model.TYPE_OTHER))
				self.append_view(view)
				found = True

			except model.CalledProcessError:
				found = False

		self.frame_widget.focus_position = "body"

		if not found:
			self.show_error(_("bad hash id {hash_id}").format(hash_id=search_text))


	def select_tag(self, prev=False):
		view = self.main_views[self.main_views_index]
		view.save_focus(self.SAVE_BEFORE_SELECT_TAG)

		hash_id, id_type = self.get_current_hash_id()

		tag = self.get_closest_tag(hash_id, prev, exclusive=True)
		if tag is None:
			return

		if id_type == model.TYPE_TAG:
			assert tag != hash_id
			view = DetailsView(model.DetailsModel(tag, model.TYPE_TAG))
			self.main_views[self.main_views_index] = view
			self.update_frame_body()

		else:
			new_hash_id = model.get_commit_hash(tag)
			self.select_commit(new_hash_id, save_focus=False)
	
	def select_first_line(self):
		self.main_views[self.main_views_index].save_focus(self.SAVE_BEFORE_MOVE_MANY)
		self.main_views[self.main_views_index].focus_first_line()

	def select_last_line(self):
		self.main_views[self.main_views_index].save_focus(self.SAVE_BEFORE_MOVE_MANY)
		self.main_views[self.main_views_index].focus_last_line()

	def select_next_section(self):
		self.main_views[self.main_views_index].save_focus(self.SAVE_BEFORE_SELECT_SECTION)
		self.main_views[self.main_views_index].focus_next_section()
	
	def select_prev_section(self):
		self.main_views[self.main_views_index].save_focus(self.SAVE_BEFORE_SELECT_SECTION)
		self.main_views[self.main_views_index].focus_prev_section()

	def select_next_paragraph(self):
		view = self.main_views[self.main_views_index]
		view.save_focus(self.SAVE_BEFORE_SELECT_PARAGRAPH)
		if hasattr(view, "focus_next_paragraph"):
			view.focus_next_paragraph()
		else:
			self.show_error(_("select next paragraph is not implemented for this view"))

	def select_prev_paragraph(self):
		view = self.main_views[self.main_views_index]
		view.save_focus(self.SAVE_BEFORE_SELECT_PARAGRAPH)
		if hasattr(view, "focus_prev_paragraph"):
			view.focus_prev_paragraph()
		else:
			self.show_error(_("select previous paragraph is not implemented for this view"))

	def select_prev_selection(self):
		self.main_views[self.main_views_index].focus_prev()

	def select_next_selection(self):
		self.main_views[self.main_views_index].focus_next()


	# ------- search bar -------

	def search_start(self, search_text, case_sensitive, is_regex):
		self.search_edit = SearchEdit(self)
		self.search_edit.set_direction(self.search_direction_reversed)
		self.search_edit.set_search_text(search_text, case_sensitive=case_sensitive, is_regex=is_regex)
		self.search_prepare(search_text, case_sensitive=case_sensitive, is_regex=is_regex)

	def search_open_edit(self, reverse=False, clear=True):
		if self.search_edit is None:
			self.search_edit = SearchEdit(self)

		if clear:
			self.search_edit.clear()
			self.search_direction_reversed = reverse
			self.search_edit.set_direction(reverse)

		self.frame_widget.footer = self.search_edit
		self.frame_widget.focus_position = "footer"

	def search_do(self, search_text, case_sensitive=None, is_regex=None):
		self.main_views[self.main_views_index].save_focus(self.SAVE_BEFORE_SEARCH)

		if case_sensitive is None:
			case_sensitive = self.search_case_sensitive
			if case_sensitive is None:
				case_sensitive = not search_text.islower()

		if is_regex is None:
			is_regex = self.search_is_regex

		if not self.search_prepare(search_text, case_sensitive=case_sensitive, is_regex=is_regex):
			return

		self.frame_widget.focus_position = "body"
		self.show_info(_('searching for "%s"') % self.search_text)
		self.search_next()

	def search_prepare(self, search_text, case_sensitive, is_regex):
		self.search_text = search_text

		if is_regex:
			flags = 0 if case_sensitive else re.IGNORECASE
			try:
				reo = re.compile(search_text, flags)
			except re.error as e:
				self.show_error(_('syntax error in search regex: %s') % e)
				return False
			self.search_cmp = lambda widget: reo.search(widget.text)
		elif case_sensitive:
			self.search_cmp = lambda widget: search_text in widget.text
		else:
			search_text = search_text.casefold()
			self.search_cmp = lambda widget: search_text in widget.text.casefold()
		return True

	def search_cancel(self):
		self.frame_widget.focus_position = "body"
		self.show_clear()

	def search_next(self, prev=False):
		if not self.search_cmp:
			self.show_error(_("nothing to search for"))
			return

		reverse = self.search_direction_reversed != prev
		found = self.main_views[self.main_views_index].search(self.search_cmp, reverse=reverse)

		if not found:
			self.show_error(_("%r not found") % self.search_text)

	def search_prev(self):
		self.search_next(prev=True)


	# ------- line numbers -------

	def line_numbers(self, fmt):
		model.DetailsModel.linenumber = fmt

		if self.state == self.STATE_RUNNING:
			for view in self.main_views:
				if isinstance(view, DetailsView):
					view.update_line_numbers(fmt)


	# ------- visual mode -------

	VISUAL_ON = 'on'
	VISUAL_OFF = 'off'
	VISUAL_TOGGLE = 'toggle'

	def visual(self, arg):
		view = self.main_views[self.main_views_index]
		if not hasattr(view, 'enable_selection'):
			self.show_error("this view does not support switching visual mode on/off")
			return

		if arg == self.VISUAL_ON:
			view.enable_selection()
		elif arg == self.VISUAL_OFF:
			view.disable_selection()
		elif arg == self.VISUAL_TOGGLE:
			view.toggle_selection()
		else:
			raise ValueError("invalid arg for visual: %r" % arg)


	# ------- open external program -------

	OPEN_AFTER = 'after'
	OPEN_BEFORE_RIGHT = 'before-right'
	OPEN_BEFORE_LEFT = 'before-left'
	OPEN_NOW = 'now'

	def open_external(self, which):
		err = model.check_editor()
		if err:
			self.show_error(err)
			return

		view = self.main_views[self.main_views_index]
		if isinstance(view, DetailsView):
			fn = view.get_current_filename()
			if fn is None:
				self.show_error(_("no file selected"))
				return

			commit = view.get_current_hash_id()[0]
			if which == self.OPEN_NOW:
				fn = model.get_relative_path(fn)
				line_number = view.get_current_line_number(which)
				self._run_external = lambda: model.open_file_in_editor(fn, line_number=line_number)
				self._reload_after_run_external = commit == self.ID_UNSTAGED
			else:
				if commit in (self.ID_UNSTAGED, self.ID_UNTRACKED) and which == self.OPEN_AFTER:
					fn = model.get_relative_path(fn)
					line_number = view.get_current_line_number(which)
					self._run_external = lambda: model.open_file_in_editor(fn, line_number=line_number, read_only=True)
					self._reload_after_run_external = False
				else:
					object_id = view.get_current_object_id(which)
					if object_id is None:
						self.show_error(_("I have no object id for the version {which}").format(which=which))
						return
					line_number = view.get_current_line_number(which)
					self._run_external = lambda: model.open_old_version_in_editor(fn, commit, object_id, which, line_number=line_number)
					self._reload_after_run_external = False
			raise urwid.ExitMainLoop()
		else:
			self.show_error(_("open is only implemented for details view"))

	def run_external_if_requested(self):
		if self._run_external:
			self._run_external()
			self._run_external = None
			self.continue_running = True
			if self.is_auto_open_enabled and self._reload_after_run_external:
				self.reload()
		elif not self.continue_running:
			self.close_command_pipe()


	def get_current_file_path(self):
		view = self.main_views[self.main_views_index]
		if isinstance(view, DetailsView):
			fn = view.get_current_filename()
			if fn:
				fn = model.get_relative_path(fn)
				return fn

			self.show_error(_("no file selected"))
			return

		self.show_error(_("getting a file path is supported by details view only"))


	# ------- log level -------

	attr_to_log_level_map = {
		ATTR_INFO : settings.LOG_LEVEL_INFO,
		ATTR_SUCCESS : settings.LOG_LEVEL_SUCCESS,
		ATTR_WARNING : settings.LOG_LEVEL_WARNING,
		ATTR_ERROR : settings.LOG_LEVEL_ERROR,
	}
	LOG_LEVEL_UNKNOWN = settings.LOG_LEVEL_NONE - 1

	def attr_matches_log_level(self, attr):
		lv = self.attr_to_log_level_map.get(attr, self.LOG_LEVEL_UNKNOWN)
		return lv >= self.log_level


	def log_level_name_to_value(self, log_level_name):
		for name, val, help in settings.iter_allowed_values(settings.LOG_LEVELS):
			if name == log_level_name:
				return val
		raise ValueError('invalid log level name: %r' % log_level_name)


	def save_and_set_log_level(self, log_level):
		self._loglevels.append(self._log_level)
		self._log_level = log_level

	def restore_log_level_if_it_has_not_been_changed(self):
		if self._loglevels:
			self._log_level = self._loglevels.pop()


	# ------- status bar -------

	def show_error(self, msg, **kw):
		if isinstance(msg, Exception):
			msg = str(msg)
		self.show(self.ATTR_ERROR, msg, **kw)

	def show_warning(self, msg, **kw):
		self.show(self.ATTR_WARNING, msg, **kw)

	def show_info(self, msg, **kw):
		self.show(self.ATTR_INFO, msg, **kw)

	def show_success(self, msg, **kw):
		self.show(self.ATTR_SUCCESS, msg, **kw)


	def show(self, attr, msg, **kw):
		if not self.attr_matches_log_level(attr):
			return

		self.messages.append((attr, msg, kw))

	def _running__show(self, attr, msg, *, contains_align_character=False, contains_color_markup=False):
		if not self.attr_matches_log_level(attr):
			return

		if urwid_text_layout.ALIGN == LogTextLayout.ALIGN_INDENTATION:
			if not contains_align_character:
				msg = model.ALIGN_CHAR + msg
		else:
			if contains_align_character:
				msg = msg.replace(model.ALIGN_CHAR, '', 1)

		if contains_color_markup:
			msg = utils.colored_str_to_markup(msg, self.define_color)

		if not isinstance(self.frame_widget.footer, urwid.Pile):
			self.frame_widget.footer = urwid.Pile([])
		widget = urwid.Text((attr,msg), align=self.align)
		self.frame_widget.footer.contents.append((widget, ('pack', None)))

	def show_clear(self):
		self.frame_widget.footer = None


	# ------- pressed keys overlay -------

	def show_mapped_commands(self, key):
		title = _("{key} is mapped to the following commands:").format(key=key)
		key = self.format_keys(self.parse_key(key))
		cmdmap = SubCommandMap()
		for ikey, cmds in HelpViewGenerator.iter_commands(self.command_map_standard, self.command_fallback):
			if ikey.startswith(key):
				self.bind_key(ikey, cmds[0], cmdmap=cmdmap)
		self.show_pressed_keys(cmdmap, "", title=title)

	def show_mapped_keys(self, cmd):
		self.show_pressed_keys(self.command_map_standard, "", title=_("{cmd} is contained in the following key mappings:").format(cmd=cmd), cmd=cmd)

	def show_pressed_keys(self, command_map, pressed_keys, *, title=None, cmd=None):
		self.is_pressed_keys_overlay_open = True
		self.frame_widget.body = OverlayPressedKeys(self.frame_widget.body, pressed_keys, command_map, self.command_fallback, title=title, cmd=cmd)

	def hide_pressed_keys(self):
		if not self.is_pressed_keys_overlay_open:
			return
		self.frame_widget.body = self.frame_widget.body.bg_widget
		self.is_pressed_keys_overlay_open = False


	# ------- help -------

	def show_introduction(self):
		view = self.main_views[self.main_views_index]
		if isinstance(view, IntroductionView):
			return
		self.append_view(IntroductionView())

	def show_keyboard_shortcuts(self):
		view = self.main_views[self.main_views_index]
		if isinstance(view, HelpView) and not view.commands:
			return
		self.append_view(HelpView(self.command_map, self.command_fallback))

	def show_available_commands(self):
		view = self.main_views[self.main_views_index]
		if isinstance(view, HelpView) and view.commands:
			return
		self.append_view(HelpView(self.command_map, self.command_fallback, commands=True))

	def show_help_for_command(self, cmd):
		view = self.main_views[self.main_views_index]
		if hasattr(view, 'save_focus'):
			view.save_focus(self.SAVE_BEFORE_GO_RIGHT)

		view = HelpDetailsView(cmd, self.command_map, self.command_fallback)
		self.append_view(view)

	def show_settings(self):
		view = self.main_views[self.main_views_index]
		if hasattr(view, 'save_focus'):
			view.save_focus(self.SAVE_BEFORE_GO_RIGHT)
		
		cmd = "set"
		view = HelpDetailsView(cmd, self.command_map, self.command_fallback)
		view.jump_to_before_render("available settings:")
		self.append_view(view)

	def parse_help(self, lines, parse_mentioned_settings=False):
		mentioned_settings = [] if parse_mentioned_settings else None
		out = []
		for ln in lines:
			out.append(self.parse_help_line(ln, mentioned_settings_out=mentioned_settings))

		if mentioned_settings is None:
			mentioned_settings = []
		return out, mentioned_settings

	reo_cmd = re.compile('`(?P<cmd>.*?)`')
	reo_var = re.compile('%(?P<var>[^ ]+?)%')
	def parse_help_line(self, ln, *, mentioned_settings_out=None):
		if isinstance(ln, AlignedLine):
			ln = ln.ln
			conv = AlignedLine
		else:
			conv = lambda x: x
		if mentioned_settings_out is not None:
			for m in self.reo_var.finditer(ln):
				setting = m.group('var')
				if '*' in setting:
					reo = re.compile(re.escape(setting).replace('*', re.escape('*')))
					for s in settings.keys():
						if s not in mentioned_settings_out:
							mentioned_settings_out.append(s)
				elif setting not in mentioned_settings_out:
					mentioned_settings_out.append(setting)
		ln = utils.replace_in_markup(ln, self.reo_cmd, self.insert_keyboardshortcuts)
		ln = conv(ln)
		return ln

	sep_shortcut = _("/")
	pattern_cmd_without_key = _("`{cmd}`")
	pattern_cmd_with_key = _("{keys} (`{cmd}`)")
	def insert_keyboardshortcuts(self, m):
		cmd = m.group('cmd')
		shortcuts = self.get_keyboardshortcuts(cmd)
		if shortcuts:
			shortcuts = utils.list_join(self.sep_shortcut, shortcuts)
			out = self.pattern_cmd_with_key
			out = utils.replace_in_markup(out, '{keys}', shortcuts)
		else:
			out = self.pattern_cmd_without_key
		out = utils.replace_in_markup(out, '{cmd}', (settings.COLOR_CMD_IN_TEXT, cmd))
		out = utils.simplify_markup(out)

		return out

	def get_keyboardshortcuts(self, cmd):
		out = []
		for shortcut, cmds in HelpViewGenerator.iter_commands(self.command_map, self.command_fallback):
			if cmd in cmds:
				out.append((settings.COLOR_KEY_IN_TEXT, shortcut))
		return out


	# ------- debug -------

	def debug_show_line_id(self):
		view = self.main_views[self.main_views_index]
		self.show_info("line id: %r" % (view.get_line_id(),))

class ColorProperty:
	def __init__(self, color):
		self.color = color
	def __get__(self, obj, objtype):
		if obj is None: return self
		return obj.get_color(self.color)
	def __set__(self, obj, value):
		obj.set_color(self.color, value)

for color in settings.COLORS:
	setattr(App, color.replace('.', '_'), ColorProperty(color))


class NotifyingColumns(urwid.Columns):

	def __init__(self, *l, **kw):
		self.on_focus_change = kw.pop('on_focus_change')
		super().__init__(*l, **kw)

	def keypress(self, size, key):
		i = self.focus_position
		out = super().keypress(size, key)
		if not out and i != self.focus_position:
			self.on_focus_change()
		return out

class NotifyingPile(urwid.Pile):

	def __init__(self, *l, **kw):
		self.on_focus_change = kw.pop('on_focus_change')
		super().__init__(*l, **kw)

	def keypress(self, size, key):
		i = self.focus_position
		out = super().keypress(size, key)
		if not out and i != self.focus_position:
			self.on_focus_change()
		return out

class HintableHelp(Hintable):

	def mark_links(self, markups):
		markups, n = utils.replace_attribute(markups, settings.COLOR_CMD_IN_TEXT, settings.COLOR_CMD_IN_LINK)
		return markups, n


class HelpViewGenerator(SelectableListbox):

	def append_shortcut_list_widgets(self, widgets, command_map, command_fallback, children_selectable, cmd=None, indentation="", pressed_keys=""):
		shortcuts = list(self.iter_commands(command_map, command_fallback))
		if cmd:
			for i in range(len(shortcuts)-1, -1, -1):
				key, commands = shortcuts[i]
				for j in range(len(commands)):
					if self.is_same_command(commands[j], cmd):
						sort_key = (commands[j], j, commands, key)
						commands[j] = (App.ATTR_CMD, commands[j])
						shortcuts[i] = (key, commands, sort_key)
						break
				else:
					del shortcuts[i]
		else:
			shortcuts = [(key, [(App.ATTR_CMD, cmd) for cmd in commands], (commands[0], key)) for key, commands in shortcuts]

		if not shortcuts:
			widgets.append(urwid.Text(indentation+_("<no shortcuts>")))
			return

		shortcuts.sort(key=lambda s: s[2])
		get_key_width = lambda s: len(s[0])
		max_key_width = get_key_width(max(shortcuts, key=get_key_width))
		for key, cmds, sort_key in shortcuts:
			widget = HelpLineView(pressed_keys, key, cmds, max_key_width, indentation=indentation)
			widget.selectable = children_selectable
			widget = DetailsAttrMap(widget)
			widgets.append(widget)

	def append_related_settings_list_widgets(self, widgets, children_selectable, cmd, indentation=""):
		keys = [key for key in settings.keys() if self.is_related_setting(key, cmd)]
		self.append_settings_list_widgets(widgets, children_selectable, keys, indentation=indentation)

	def append_settings_list_widgets(self, widgets, children_selectable, keys, indentation=""):
		if not keys:
			return

		max_key_width = len(max(keys, key=len))
		for key in keys:
			try:
				attr, allowed_values, help_str = settings.get(key)
			except KeyError:
				self.app.show_error(_("setting %{key}% does not exist").format(key=key))
				continue
			value = settings.rgetattr(self, attr)
			ln = indentation + key.ljust(max_key_width) + HelpLineView.CMD_SEP + model.ALIGN_CHAR + settings.format_value(value, allowed_values)
			widget = DetailsLineView(ln, align=LogTextLayout.ALIGN_INDENTATION)
			widget.selectable = children_selectable
			widget = DetailsAttrMap(widget)
			widgets.append(widget)

	def is_related_setting(self, key, cmd):
		cmd, args = self.app.commands.split_cmd_args(cmd)
		return key.startswith(cmd + settings.GROUP_SEP) or key.startswith("color" + settings.GROUP_SEP + cmd + settings.GROUP_SEP) or key == "color" + settings.GROUP_SEP + cmd

	@classmethod
	def iter_commands(cls, command_map, command_fallback):
		for key in iter_commandmap_keys(command_map):
			cmd = command_map[key]
			key = App.format_key(key)
			if isinstance(cmd, SubCommandMap):
				key_prefix = key
				for key, cmds in cls.iter_commands(cmd, command_fallback):
					key = key_prefix + App.KEY_SEP + key
					yield key, cmds
			else:
				fallback = command_fallback[cmd]
				if fallback is None:
					cmds = [cmd]
				else:
					cmds = [cmd, fallback]
				yield key, cmds

	def is_same_command(self, cmd1, cmd2):
		split_cmd_args = self.app.commands.split_cmd_args
		cmd1, args1 = split_cmd_args(cmd1)
		cmd2, args2 = split_cmd_args(cmd2)
		return cmd1 == cmd2 and args1.startswith(args2)

	def append_command_list_widgets(self, widgets, children_selectable):
		for title, commands in (
			(_("programmable commands:"), self.iter_programmable_commands()),
			(_("primitive commands:"), self.iter_primitive_commands()),
		):
			widgets.append(urwid.Text((App.ATTR_SUBTITLE, title)))
			for cmd in commands:
				ln = "%s" % cmd
				widget = HelpDetailsLineView(ln)
				widget.cmd = cmd
				widget.selectable = children_selectable
				widget = DetailsAttrMap(widget)
				widgets.append(widget)
			widgets.append(urwid.Text(""))

	def iter_programmable_commands(self):
		return sorted(self.app.commands.commands.keys())
	
	def iter_primitive_commands(self):
		return sorted(set(self.app.commands.split_cmd_args(cmd)[0] for cmd in App.primitive_commands))


class FocusIndicatorView(urwid.LineBox):

	def __init__(self, original_widget, *args, **kw):
		super().__init__(original_widget, *args, **kw)
		self.unfocused_widget = urwid.LineBox(original_widget,
			tlcorner=' ', tline=' ', trcorner=' ',
			lline=' ',               rline=' ',
			blcorner=' ', bline=' ', brcorner=' ',
		)
	
	def render(self, size, focus=False):
		if focus:
			return super().render(size, focus=focus)
		return self.unfocused_widget.render(size, focus=self.app.show_focus_in_all_views)


class HelpView(HelpViewGenerator, HintableHelp):

	def __init__(self, command_map, command_fallback, commands=False):
		self.command_map_to_show = command_map
		self.command_fallback_to_show = command_fallback
		self.commands = commands
		widgets = []
		how_to_open = \
			_("use `cursor down` and `cursor up` to select {what}") + "\n" + \
			_("use `go details` or `activate` to show details") + "\n" + \
			_("use `go left` to return") + "\n"
		if commands:
			how_to_open = how_to_open.format(what=_("a command"))
			how_to_open = self.app.parse_help_line(how_to_open)
			widgets.append(HelpDetailsLineView((App.ATTR_TITLE, _("list of available commands"))))
			widgets.append(HelpDetailsLineView(how_to_open))
			self.append_command_list_widgets(widgets, self.children_selectable)
		else:
			how_to_open = how_to_open.format(what=_("a shortcut"))
			how_to_open = self.app.parse_help_line(how_to_open)
			widgets.append(HelpDetailsLineView((App.ATTR_TITLE, _("list of keyboard shortcuts"))))
			widgets.append(HelpDetailsLineView(how_to_open))
			self.append_shortcut_list_widgets(widgets, command_map, command_fallback, self.children_selectable)
		body = urwid.SimpleFocusListWalker(widgets)
		super().__init__(body)
		self.enable_selection()
		self.focus_first_line()


	def has_details(self):
		return True

	def get_current_commands(self):
		widget = self.focus.base_widget
		if hasattr(widget, 'cmd'):
			cmd = widget.cmd
			return [cmd]

		if not hasattr(widget, 'cmds'):
			return None

		cmds = widget.cmds
		cmds = [c if isinstance(c, str) else c[1] for c in cmds]
		return cmds

	def create_details_view(self):
		cmds = self.get_current_commands()
		if not cmds:
			return None

		if len(cmds) == 1:
			cmd = cmds[0]
			return self.create_help_details_view(cmd)

		widget = OverlayChoiceBox(self, _("for which command do you want to see the help?"), cmds)
		widget.create_details_view = lambda: self.create_help_details_view(widget.get_selected_command())
		return widget
	
	def create_help_details_view(self, cmd):
		return HelpDetailsView(cmd, self.command_map_to_show, self.command_fallback_to_show)

	def is_correct_details_view(self, other):
		cmds = self.get_current_commands()
		if not cmds:
			return False
		if len(cmds) == 1:
			return isinstance(other, HelpDetailsView) and other.cmd == cmds[0]
		return isinstance(other, OverlayChoiceBox) and other.choices == cmds

	def focus_next_section(self):
		start = self.focus_position

		last_selectable = start
		last_cmd = None
		for i in range(start, len(self.body)):
			widget = self.body[i].base_widget
			if not hasattr(widget, 'cmds'):
				continue
			last_selectable = i
			cmd = self.split_cmd(widget.cmds[0])
			if last_cmd is not None and last_cmd != cmd:
				break
			last_cmd = cmd

		self.enable_selection()
		self.set_focus(last_selectable)

	def focus_prev_section(self):
		start = self.focus_position
		if start <= 0:
			return

		last_selectable = start
		last_cmd = None
		for i in range(start-1, -1, -1):
			widget = self.body[i].base_widget
			if not hasattr(widget, 'cmds'):
				continue
			cmd = self.split_cmd(widget.cmds[0])
			if last_cmd is not None and cmd != last_cmd:
				break
			last_selectable = i
			last_cmd = cmd

		self.enable_selection()
		self.set_focus(last_selectable)

	def split_cmd(self, cmd_markup):
		if isinstance(cmd_markup, tuple):
			cmd = cmd_markup[1]
		else:
			cmd = cmd_markup
		return self.app.commands.split_cmd_args(cmd)[0]


	focus_next_paragraph = focus_next_section
	focus_prev_paragraph = focus_prev_section


class OverlayChoiceBox(urwid.Overlay):

	MIN_WIDTH = 30
	MIN_HEIGHT = 3

	BORDER = 1

	ATTR = App.ATTR_CMD


	@property
	def bottom_w(self):
		if self.app.view_mode == App.VIEW_MODE_ONE:
			return self.bottom_w_stacked

		if not self.bottom_w_side_by_side:
			self.bottom_w_side_by_side = urwid.SolidFill()
		return self.bottom_w_side_by_side

	@bottom_w.setter
	def bottom_w(self, w):
		pass


	def __init__(self, bg_widget, title, choices, **kw):
		'''additionally you need to set a create_details_view function'''
		self.title = title
		self.choices = choices

		widgets = []

		# title
		create_widget = HelpDetailsLineView
		self.title_widget = create_widget(self.title)
		widgets.append(self.title_widget)

		# choices
		for item in choices:
			widget = create_widget((self.ATTR, item))
			widget.selectable = self.children_selectable
			widget.cmd = item
			widget = DetailsAttrMap(widget)
			widgets.append(widget)

		self.listbox = SelectableListbox(widgets)
		self.listbox.enable_selection()

		fg_widget = urwid.LineBox(self.listbox)

		self.bottom_w_stacked = bg_widget
		self.bottom_w_side_by_side = None

		kw.setdefault('align', urwid.CENTER)
		kw.setdefault('valign', urwid.MIDDLE)
		kw.setdefault('width', self.get_width())
		kw.setdefault('height', self.get_height())
		super().__init__(fg_widget, bg_widget, **kw)

	def children_selectable(self):
		return self.listbox.children_selectable()

	def get_selected_command(self):
		view = self.listbox.focus.base_widget
		if hasattr(view, 'cmd'):
			return view.cmd
		return None

	def has_details(self):
		return self.get_selected_command()

	def get_internal_width(self):
		out = len(max(self.choices, key=len))
		if out < self.MIN_WIDTH:
			out = self.MIN_WIDTH
		return out

	def get_width(self):
		out = self.get_internal_width()
		out += 2*self.BORDER
		return out

	def get_height(self):
		out = len(self.choices)
		out += self.title_widget.rows((self.get_internal_width(),))
		if out < self.MIN_HEIGHT:
			out = self.MIN_HEIGHT
		out += 2*self.BORDER
		return out

	def disable_selection(self):
		self.app.show_error("this view does not support switching visual mode off")

	def toggle_selection(self):
		self.app.show_error("this view does not support toggling visual mode")

	def keypress(self, size, key):
		if self._command_map[key] == CANCEL:
			self.app.go_left()
			return
		return self.listbox.keypress(size, key)

	def __getattr__(self, attr):
		return getattr(self.listbox, attr)


class HelpLineView(DetailsLineView):

	CMD_SEP = '  '
	FALLBACK_SEP = ' || '

	def __init__(self, key_prefix, key, cmds, max_key_width, indentation=""):
		self.key = key
		self.cmds = cmds
		key = key.ljust(max_key_width, " ")
		# [1] because cmds[0] is an urwid markup
		mnemonic = getattr(cmds[0][1], 'mnemonic', None)
		cmds = [self.replace_special_characters_in_markup(c) for c in cmds]
		key_markup = []
		if key_prefix:
			key_markup.append((settings.COLOR_KEY_PRESSED, key_prefix))
		key_markup.append((App.ATTR_KEY, key))
		ln = [key_markup, self.CMD_SEP, model.ALIGN_CHAR, cmds[0]]
		for cmd in cmds[1:]:
			ln.append(self.FALLBACK_SEP)
			ln.append(cmd)
		if mnemonic:
			mnemonic = self.app.pattern_mnemonic.format(mnemonic=mnemonic)
			ln.append((settings.COLOR_MNEMONIC, mnemonic))
		if indentation:
			ln.insert(0, indentation)
		super().__init__(ln, align=LogTextLayout.ALIGN_INDENTATION)

	def replace_special_characters_in_markup(self, markup):
		if isinstance(markup, str):
			return self.replace_special_characters(markup)
		else:
			assert len(markup) == 2
			return (markup[0], self.replace_special_characters(markup[1]))

	def replace_special_characters(self, cmd):
		cmd = re.split("(\n|\t)", cmd)
		for i in range(len(cmd)):
			if i % 2:
				c = cmd[i]
				if c == '\n':
					c = r'\n'
				elif c == '\t':
					c = r'\t'
				else:
					assert False, "unexpected value for c: %r" % c
				cmd[i] = (App.ATTR_SPECIAL_CHARACTER, c)
		return cmd

class HelpDetailsView(HelpViewGenerator, HintableHelp):

	INDENTATION = "  "

	def __init__(self, cmd, command_map, command_fallback):
		self.cmd = cmd
		self.command_map_to_show = command_map
		self.command_fallback_to_show = command_fallback
		help_text, mentioned_settings = self.app.commands.get_help(cmd)
		lines = []
		tmp = model.NameSpace()
		tmp.last_ln = None

		POSITIONAL_ARGUMENTS = 'pos'
		OPTIONAL_ARGUMENTS = 'opt'
		self._section_type = None
		def append(ln):
			if ln and isinstance(ln, str) and not ln[0].isspace() and ln[-1] == ':' and tmp.last_ln is not None and not tmp.last_ln:
				ln = (App.ATTR_SUBTITLE, ln)
				self._section_type = None
			if ln and isinstance(ln, str) and ln[0].isspace():
				if self._section_type is None:
					if ln.lstrip()[:1] == '-':
						self._section_type = OPTIONAL_ARGUMENTS
					else:
						self._section_type = POSITIONAL_ARGUMENTS
				if self._section_type == OPTIONAL_ARGUMENTS:
					m = re.search(r'\s[^-\s]', ln)
					offset = -1
				else:
					m = re.search(r'\s\S+\s+\b', ln)
					offset = 0
				if m is not None:
					i = m.end() + offset
					ln = AlignedLine(ln[:i] + model.ALIGN_CHAR + ln[i:])
			if isinstance(ln, AlignedLine):
				widget = HelpDetailsLineView(ln.ln, align=LogTextLayout.ALIGN_INDENTATION)
			else:
				widget = HelpDetailsLineView(ln)
			widget.selectable = self.children_selectable
			widget = DetailsAttrMap(widget)
			lines.append(widget)
			tmp.last_ln = ln
		append((App.ATTR_TITLE, _("command {cmd}").format(cmd=cmd)))

		for ln in help_text:
			append(ln)

		settings_lines = []
		self.append_related_settings_list_widgets(settings_lines, self.children_selectable, cmd=cmd, indentation=self.INDENTATION)
		if settings_lines:
			append("")
			append(_("related settings:"))
			lines.extend(settings_lines)

		mentioned_settings_lines = []
		self.append_settings_list_widgets(mentioned_settings_lines, self.children_selectable, mentioned_settings, indentation=self.INDENTATION)
		if mentioned_settings_lines:
			append("")
			append(_("mentioned settings:"))
			lines.extend(mentioned_settings_lines)

		append("")
		append(_("keyboard shortcuts for this command:"))
		if self.app.help_show_all_shortcuts:
			cmd = self.app.commands.split_cmd_args(cmd)[0]
		self.append_shortcut_list_widgets(lines, self.command_map_to_show, self.command_fallback_to_show, self.children_selectable, cmd=cmd, indentation=self.INDENTATION)

		super().__init__(lines)

	def focus_next_paragraph(self):
		was_last_empty_line = None
		for i in range(self.focus_position, len(self.body)):
			widget = self.body[i].base_widget
			is_empty_line = not widget.text.strip()
			if was_last_empty_line and not is_empty_line:
				self.enable_selection()
				self.set_focus(i)
				return

			was_last_empty_line = is_empty_line

		self.enable_selection()
		self.set_focus(i)

	def focus_prev_paragraph(self):
		was_last_empty_line = True
		for i in range(self.focus_position-1, -1, -1):
			widget = self.body[i].base_widget
			is_empty_line = not widget.text.strip()
			if not was_last_empty_line and is_empty_line:
				self.enable_selection()
				self.set_focus(i+1)
				return

			was_last_empty_line = is_empty_line

		self.enable_selection()
		self.set_focus(0)

	def jump_to_before_render(self, text):
		for i in range(0, len(self.body)):
			widget = self.body[i].base_widget
			if widget.text == text:
				self.on_render = lambda size, focus: self.change_focus(size, i, offset_inset=0)
				return
	
	def render(self, size, focus=False):
		if getattr(self, 'on_render', None):
			self.on_render(size, focus)
			self.on_render = None
		return super().render(size, focus)


class HelpDetailsLineView(LineView):

	pass


class IntroductionView(SelectableListbox, HintableHelp):

	fn = os.path.join('doc', 'intro.md')

	section = '# '

	def __init__(self):
		self.fn = os.path.join(os.path.split(os.path.realpath(__file__))[0], self.fn)
		body = []
		body.append(self.create_line_view((settings.COLOR_TITLE, _("help"))))
		body.extend(self.get_version())
		with open(self.fn, 'rt') as f:
			body.extend(self.parse(f))
		super().__init__(body)

	def create_line_view(self, ln, **kw):
		widget = IntroLineView(ln, **kw)
		widget.selectable = self.children_selectable
		widget = DetailsAttrMap(widget)
		return widget

	def get_version(self):
		yield self.create_line_view(_("{appname} version {version}").format(appname=App.APP_NAME, version=__version__))
		yield self.create_line_view("")

	def parse(self, lines):
		out = []
		len_section = len(self.section)
		is_in_section = False
		for ln in lines:
			ln = ln.rstrip()
			if ln.startswith(self.section):
				attr = settings.COLOR_SUBTITLE
				ln = ln[len_section:]
				ln = model.ALIGN_CHAR + ln
				is_in_section = True
			else:
				attr = None
				if is_in_section:
					indentation = "  "
				else:
					indentation = ""
				ln = indentation + model.ALIGN_CHAR + ln
			ln = ln.replace("\t", DetailsView.TAB)
			ln = self.app.parse_help_line(ln)
			if attr:
				ln = (attr, ln)
			yield self.create_line_view(ln, align=LogTextLayout.ALIGN_INDENTATION)

	def focus_next_section(self):
		start = self.focus_position
		stop = len(self.body)
		for i in range(start+1, stop):
			widget = self.body[i].base_widget
			if widget.attr == settings.COLOR_SUBTITLE:
				break
		else:
			i = stop - 1

		self.enable_selection()
		self.set_focus(i)

	def focus_prev_section(self):
		start = self.focus_position
		for i in range(start-1, -1, -1):
			widget = self.body[i].base_widget
			if widget.attr == settings.COLOR_SUBTITLE:
				break
		else:
			i = 0

		self.enable_selection()
		self.set_focus(i)

	focus_next_paragraph = focus_next_section
	focus_prev_paragraph = focus_prev_section

class IntroLineView(LineView):

	def __init__(self, ln, **kw):
		if isinstance(ln, tuple):
			self.attr = ln[0]
		else:
			self.attr = None
		super().__init__(ln, **kw)


class OverlayPressedKeys(urwid.Overlay):

	BORDER_LEFT = 0
	BORDER_RIGHT = 3
	BORDER_VER = 1


	class BgContainer(urwid.WidgetWrap):

		def __init__(self, master, widget):
			self.master = master
			super().__init__(widget)

		def render(self, size, focus=False):
			return self._w.render(size, self.master.is_focused)


	def __init__(self, bg_widget, pressed_keys, command_map, command_fallback, *, title=None, cmd=None):
		self.bg_widget = bg_widget
		self.listbox = PressedKeysWidget(pressed_keys, command_map, command_fallback, title=title, cmd=cmd)

		header = urwid.Text("")
		self.frame = urwid.Frame(self.listbox, header=header)
		self.fg_widget = urwid.Padding(self.frame, left=self.BORDER_LEFT, right=self.BORDER_RIGHT)

		kw = {
			'align': urwid.LEFT,
			'valign': urwid.BOTTOM,
			'width': self.get_width(),
			'height': self.get_height(),
		}

		bottom_w = self.BgContainer(self, self.bg_widget)
		super().__init__(self.fg_widget, bottom_w, **kw)

	def get_width(self):
		out = self.listbox.get_width()
		out += self.BORDER_LEFT + self.BORDER_RIGHT
		return out

	def get_height(self):
		out = self.listbox.get_height()
		out += self.BORDER_VER
		return out

	def keypress(self, size, key):
		return key

	def render(self, size, focus=False):
		self.is_focused = focus
		return super().render(size, focus)


class PressedKeysWidget(HelpViewGenerator):

	MAX_WIDTH = 40

	ELLIPSIS = _('...')

	def __init__(self, pressed_keys, command_map, command_fallback, *, title=None, cmd=None):
		self.command_map_to_show = command_map
		self.command_fallback_to_show = command_fallback

		widgets = []
		if title:
			widgets.append(urwid.Text((App.ATTR_TITLE, title)))
		self.append_shortcut_list_widgets(widgets, command_map, command_fallback, self.children_selectable, pressed_keys=pressed_keys, cmd=cmd)
		self.ellipsis_widget = urwid.Text((App.ATTR_ELLIPSIS, self.ELLIPSIS), align=urwid.CENTER)

		body = urwid.SimpleFocusListWalker(widgets)
		super().__init__(body)

		self.size = self.calc_size()

	def calc_size(self):
		if self.MAX_WIDTH:
			max_width = self.MAX_WIDTH
		else:
			max_width = self.app.screen.get_cols_rows()[0]

		width, height = 0, 0
		for widget in self.body:
			line_width, line_height = measure_text_size(widget, max_width)
			if line_width > width:
				width = line_width
			height += line_height

		return width, height

	def get_height(self):
		return self.size[1]

	def get_width(self):
		return self.size[0]


	def render(self, size, *args, **kw):
		bottom_c = super().render(size, *args, **kw)
		if self.all_shortcuts_visible(size):
			return bottom_c

		top_c = self.ellipsis_widget.render((size[0],))
		top_c = urwid.CompositeCanvas(top_c)
		left = 0
		top = size[1] - 1
		return urwid.CanvasOverlay(top_c, bottom_c, left, top)

	def all_shortcuts_visible(self, size):
		middle, top, bottom = self.calculate_visible(size)
		number_visible_widgets = len(top[1]) + len(bottom[1]) + bool(middle)
		return number_visible_widgets == len(self.body)


def process_args(args):
	diff_args = []

	for key in ("--diff-options", "-d"):
		try:
			i = args.index(key)
			diff_args = args[i+1:]
			args = args[:i]
			break
		except ValueError:
			pass

	log_args = args

	return log_args, diff_args

def parse_common_args(args, *, doc):
	if "--help" in args or "-h" in args:
		print_help(doc)
		exit()
	if "--version" in args:
		print_version()
		exit()

	out = {}

	FLAG_OPEN_ALWAYS = "--open-always"
	if FLAG_OPEN_ALWAYS in args:
		args.remove(FLAG_OPEN_ALWAYS)
		out['open_always'] = True
	else:
		out['open_always'] = False

	out['config_file'] = get_arg_with_one_argument(args, "--config")
	out['command_pipe'] = get_arg_with_one_argument(args, "--command-pipe")
	api_subprocess.gitdir = get_arg_with_one_argument(args, "--git-dir")
	api_subprocess.worktree = get_arg_with_one_argument(args, "--work-tree")

	return out

def get_arg_with_one_argument(args, name, default=None, allowed_values=None):
	n = len(args)
	for i in range(n):
		a = args[i]
		if a.startswith(name):
			if a == name:
				if i + 1 >= n:
					print(_("missing value for %s") % name)
					exit(1)
				value = args[i+1]
				del args[i]
				del args[i]
				break

			j = a.find("=")
			if j == len(name):
				value = a[j+1:]
				del args[i]
				break

	else:
		return default

	if allowed_values and value not in allowed_values:
		print(_("invalid value for %s: %r") % (name, value))
		print(_("allowed values: %s") % _(", ").join(allowed_values))
		exit(1)

	return value


def print_help(doc):
	doc = doc.strip("\n")
	doc = doc.replace("{doc_common_options}", doc_common_options.strip("\n"))
	print(doc)

def get_version():
	fn = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'doc', 'version.txt')
	with open(fn, 'rt') as f:
		return f.read().rstrip()

__version__ = get_version()

def print_version():
	import sys
	thisversion = _("{appname} version {version}").format(appname=App.APP_NAME, version=__version__)
	gitver = model.get_git_version().replace("\n", " ")
	pyver = _("python version ") + sys.version.replace("\n", " ")
	urwidver = _("urwid version %s") % ".".join(str(i) for i in urwid.VERSION)
	print(thisversion, pyver, urwidver, gitver, sep="\n")


def run():
	import sys
	args = sys.argv[1:]

	FLAG_UNREACHABLE = "--unreachable"

	kw = parse_common_args(args, doc=__doc__)
	log_args, diff_args = process_args(args)

	if FLAG_UNREACHABLE in log_args:
		unreachable = True
		i = log_args.index(FLAG_UNREACHABLE)
		unreachable_args = log_args[i+1:]
		log_args = log_args[:i]
	else:
		unreachable = False
		unreachable_args = []

	a = App(show_unreachable=unreachable, log_args=log_args, unreachable_args=unreachable_args, diff_args=diff_args, **kw)
	while a.continue_running:
		a.run()
		a.run_external_if_requested()


if __name__ == '__main__':
	run()
