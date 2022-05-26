#!/usr/bin/env python

import os
import stat
import tempfile
import re
import shlex
import shutil
import gettext
_ = gettext.gettext

from .api_subprocess import Runner, CommandError
from .string_formatter import formatter
from .color_decoder import ColorDecoder
from . import utils
from . import settings

ALIGN_CHAR = "^"

ID_UNTRACKED = "<untracked>"
ID_UNSTAGED = "<unstaged>"
ID_STAGED = "<staged>"
ID_STASHES_GROUP = "<stashed>"
SPECIAL_IDS = (ID_UNTRACKED, ID_UNSTAGED, ID_STAGED, ID_STASHES_GROUP)

TYPE_STASHED = "stashed"
TYPE_OTHER = "other"
TYPE_ERROR = "error"
TYPE_TAG = "tag"
TYPE_START_OF_FILE = "sof"
TYPE_NUMBERED_LINE = "numbered-line"
TYPE_UNTRACKED = "untracked"

#https://matthew-brett.github.io/curious-git/git_object_types.html
OBJECT_TYPE_COMMIT = "commit"
OBJECT_TYPE_TREE = "tree"
OBJECT_TYPE_BLOB = "blob"
OBJECT_TYPE_TAG = "tag"

FLAG_CUSTOM_FORMAT = "--custom-format"
FORMAT_PREFIX = "--pretty=format:"

title_untracked = _('New files, uncommitted and not checked in to index')
title_unstaged = _('Local uncommitted changes, not checked in to index')
title_unstaged_and_untracked = formatter.format(_('{title_unstaged} and {title_untracked:l}'), title_unstaged=title_unstaged, title_untracked=title_untracked)
title_staged   = _('Local changes checked in to index but not committed')
title_stashes_group = _('{number} stashes')
title_referencedby = _('This commit is referenced by the following commits:')
title_commit = _("commit {hash_id}{refnames}")
pattern_refnames = _(" ({refnames})")
refnames_sep = _(", ")

error_no_unreachable_commits = _('no unreachable commits')


# ---------- model classes ----------

class NameSpace:
	pass

class FileInfo:
	__slots__ = ('fn', 'object_id_before_left', 'object_id_before_right', 'object_id_after')

	def __init__(self, fn=None):
		self.fn = fn
		self.object_id_before_left = None
		self.object_id_before_right = None
		self.object_id_after = None

class LineInfo:
	__slots__ = ('linenumber_after', 'linenumber_before_right', 'linenumber_before_left',
		'formatted_linenumber_after', 'formatted_linenumber_before_right', 'formatted_linenumber_before_left',
		'is_modified')

	def __repr__(self):
		args = ", ".join("%s" % getattr(self, a) for a in ('linenumber_after', 'linenumber_before_right', 'linenumber_before_left'))
		return "%s(%s)" % (type(self).__name__, args)


class Model(Runner):

	"""
	A command is a list of strings as expected by the subprocess library
	or a list of such commands. If several commands are given they are
	executed one after another and their outputs are concatenated.
	_append_cmd, _remove_cmd and _toggle_cmd operate on the last command only.
	"""

	CARRIAGE_RETURN = '' #r'\r'

	cmd = None

	# commands starting with this prefix are not executed as shell commands
	# but looked up in command_functions
	INTERNAL_FUNCTION_PREFIX = "$"

	command_functions = dict()


	# ------- generate output -------

	def get_lines(self):
		if self.are_several_commands(self.cmd):
			out = list()
			for cmd in self.cmd:
				out.extend(self._get_lines(cmd))
		else:
			cmd = self.cmd
			out = self._get_lines(cmd)

		return out

	def _get_lines(self, cmd):
		i = len(self.INTERNAL_FUNCTION_PREFIX)
		if cmd[0][:i] == self.INTERNAL_FUNCTION_PREFIX:
			fun = cmd[0][i:]
			try:
				fun = self.command_functions[fun]
			except KeyError as e:
				supported_commands =  ", ".join(key for key in sorted(self.command_functions.keys()))
				raise CommandError(cmd, "no such internal command %r, should be one of %s" % (fun, supported_commands))
			args = cmd[1:]
			return fun(self, args)

		return self.run_and_get_output(cmd).replace('\r', self.CARRIAGE_RETURN).splitlines()


	# ------- manipulate commands -------

	@classmethod
	def replace_in_cmd(cls, cmd, wildcard, value):
		if not cls.are_several_commands(cmd):
			cmd = [cmd]

		return [[value if x == wildcard else x for x in subcmd] for subcmd in cmd]

	@classmethod
	def replace_characters_in_cmd(cls, cmd, old, new, count=-1):
		"""
		count = -1: replace all occurences of old with new
		count > -1: replace the first count occurences of old with new
		            in the first argument where old appears of every subcommand
		"""
		if cls.are_several_commands(cmd):
			return [cls.replace_characters_in_subcmd(subcmd, old, new, count) for subcmd in cmd]
		else:
			return cls.replace_characters_in_subcmd(cmd, old, new, count)

	@classmethod
	def replace_characters_in_subcmd(cls, subcmd, old, new, count=-1):
		out = []
		unfinished = True
		for arg in subcmd:
			if unfinished and old in arg:
				arg = arg.replace(old, new, count)
				if count >= 0:
					unfinished = False
			out.append(arg)
		return out


	def replace_custom_format(self, cmd):
		if not self.are_several_commands(cmd):
			cmd = [cmd]

		out = []
		for subcmd in cmd:
			if "-g" in subcmd or "--walk-reflogs" in subcmd:
				subcmd = [FORMAT_PREFIX + self.fmt_reflog if w == FLAG_CUSTOM_FORMAT else w for w in subcmd]
				if subcmd[-1][:1] == '-':
					subcmd.append('HEAD@{0}')
			else:
				subcmd = [FORMAT_PREFIX + self.fmt_log if w == FLAG_CUSTOM_FORMAT else w for w in subcmd]
			out.append(subcmd)
		return out


	@staticmethod
	def are_several_commands(cmd):
		return isinstance(cmd[0], list)

	@classmethod
	def _append_cmd(cls, cmd, options):
		if cls.are_several_commands(cmd):
			cmd[-1].extend(options)
		else:
			cmd.extend(options)

	@classmethod
	def _remove_cmd(cls, cmd, options):
		if cls.are_several_commands(cmd):
			cmd = cmd[-1]
		for opt in options:
			while opt in cmd:
				cmd.remove(opt)

	@classmethod
	def _toggle_cmd(cls, cmd, options):
		if cls.are_several_commands(cmd):
			cmd = cmd[-1]

		count_added = 0
		count_removed = 0
		for opt in options:
			if opt in cmd:
				while opt in cmd:
					cmd.remove(opt)
					count_removed += 1
			else:
				cmd.append(opt)
				count_added += 1

		return count_added, count_removed

	@classmethod
	def _copy_command(cls, cmd):
		if cls.are_several_commands(cmd):
			return [list(c) for c in cmd]
		return list(cmd)


	# ------- branches ------

	_local_branches=None
	def get_local_branches(self):
		cls = type(self)
		if cls._local_branches is None:
			cls._local_branches = self._get_branches()
		return cls._local_branches

	_remote_branches=None
	def get_remote_branches(self):
		cls = type(self)
		if cls._remote_branches is None:
			cls._remote_branches = self._get_branches("--remote")
		return cls._remote_branches

	def _get_branches(self, arg=None):
		cmd = ["git", "branch"]
		if arg:
			cmd.append(arg)

		stdout = self.run_and_get_output(cmd).splitlines()
		return [ln[2:] for ln in stdout]

	@classmethod
	def clear_cache(cls):
		cls._local_branches = None
		cls._remote_branches = None



class LogModel(Model):

	fmt_log    = "%Cred%h%Creset -^%C(yellow)%d%Creset %s %Cgreen(%cd) %C(bold blue)<%an>%Creset"
	fmt_reflog = "%Cred%h %Creset%C(yellow)%gD%Creset^%C(yellow)%d%Creset %gs %Cgreen(%cd) %C(bold blue)<%gn>%Creset"

	cmd_log = [["$status"], ["git", "log", "--color", "--graph", "--date=relative", FLAG_CUSTOM_FORMAT, "--abbrev-commit"]]
	cmd_stash_list = ["git", "stash", "list", "--color", "--pretty=format:%C(cyan)* %Cred%gd%Creset - ^%s %Cgreen(%cr)%Creset", "--abbrev-commit"]
	cmd_unreachable = ["git", "fsck", "--unreachable"]

	@classmethod
	def append_cmd_log(cls, options):
		cmd = cls.cmd_log
		if cls.are_several_commands(cmd):
			cmd = cmd[-1]

		if "--no-walk" in options and "--graph" in cmd:
			cmd.remove("--graph")
		elif ("-g" in options or "--walk-reflogs" in options) and "--graph" in cmd:
			cmd.remove("--graph")

		while "--no-graph" in options:
			# remove all occurences of --graph in cmd
			while "--graph" in cmd:
				cmd.remove("--graph")

			# remove all occurences of --graph in options before --no-graph
			i_no_graph = options.index("--no-graph")
			del options[i_no_graph]
			while True:
				try:
					i = options.index("--graph", 0, i_no_graph)
				except ValueError:
					break
				else:
					del options[i]
					i_no_graph -= 1

		cmd.extend(options)

	@classmethod
	def remove_cmd_log(cls, options):
		cls._remove_cmd(cls.cmd_log, options)

	@classmethod
	def toggle_cmd_log(cls, options):
		return cls._toggle_cmd(cls.cmd_log, options)


	def remove_align_character(self):
		align_char = ALIGN_CHAR
		cls = type(self)
		self.fmt_log = cls.fmt_log.replace(align_char, "", 1)
		self.fmt_reflog = cls.fmt_reflog.replace(align_char, "", 1)

		self.cmd_log = self.replace_characters_in_cmd(cls.cmd_log, align_char, "", 1)
		self.cmd_stash_list = self.replace_characters_in_cmd(cls.cmd_stash_list, align_char, "", 1)

		self.ln_pattern = cls.ln_pattern.replace(align_char, "", 1)
		self.ln_pattern_error = cls.ln_pattern_error.replace(align_char, "", 1)

	def restore_align_character(self):
		cls = type(self)
		self.fmt_log = cls.fmt_log
		self.fmt_reflog = cls.fmt_reflog

		self.cmd_log = cls.cmd_log
		self.cmd_stash_list = cls.cmd_stash_list

		self.ln_pattern = cls.ln_pattern
		self.ln_pattern_error = cls.ln_pattern_error

	WC_LOGENTRY = '{logentry}'
	ln_pattern = '* ^<color=default>' + WC_LOGENTRY
	ln_pattern_error = '\n<color=%color.echo.error%>{err}</color>\nsee %{setting}%\ncmd = {cmd}\n'

	show_untracked = True
	untracked_files_as_separate_group = False

	show_stashed_changes = True
	stashed_changes_reversed_order = False
	stashed_changes_group = None  # True|False|None. None = auto

	re_hex = r'[0-9A-F]'
	reo_hash_id = re.compile(r"(?:\b|(?<=m))(%(re_hex)s{7,40})\b" % dict(re_hex=re_hex), re.IGNORECASE)
	reo_stash_id = re.compile(r"stash@\{\d+\}", re.IGNORECASE)

	def get_lines(self):
		"""return a list of 3-tuples (line, id, type), each representing one line"""
		# committed changes
		self.cmd = self.cmd_log
		self.cmd = self.replace_custom_format(self.cmd)
		try:
			lines = super().get_lines()
		except CommandError as e:
			log = self.format_command_error(e, setting='log-view.cmd.log')
		else:
			log = lines
			log = [(ln, self.extract_hash_id(ln), TYPE_OTHER) if isinstance(ln, str) else ln for ln in log]

		return log

	def format_command_error(self, e, setting):
		ln = self.ln_pattern_error.format(err=e.err, cmd=e.cmd, setting=setting)
		ln = utils.colored_str_to_markup(ln, self.app.define_color)
		return [(ln, None, TYPE_ERROR)]

	def status(self, args):
		# uncommitted changes
		if args:
			cmd = ['$status'] + args
			raise CommandError(cmd, "status takes no arguments")

		self.cmd = ["git", "status", "--porcelain=v1"]
		status = super().get_lines()

		untracked = False
		unstaged = False
		staged = False

		# X: index
		# Y: work tree
		for ln in status:
			if ln[0] not in ' !?':
				staged = True
			if ln[1] not in ' !?':
				unstaged = True
			if ln[:2] == '??':
				untracked = True

		if not self.show_untracked:
			untracked = False

		log = []
		if staged:
			ln = self.format_log_entry(settings.COLOR_LOG_STAGED, title_staged)
			log.insert(0, (ln, ID_STAGED, TYPE_OTHER))

		if unstaged:
			if untracked and not self.untracked_files_as_separate_group:
				title = title_unstaged_and_untracked
				untracked = False
			else:
				title = title_unstaged
			ln = self.format_log_entry(settings.COLOR_LOG_UNSTAGED, title)
			log.insert(0, (ln, ID_UNSTAGED, TYPE_OTHER))

		if untracked:
			ln = self.format_log_entry(settings.COLOR_LOG_UNTRACKED, title_untracked)
			log.insert(0, (ln, ID_UNTRACKED, TYPE_OTHER))


		# stashed changes
		if self.show_stashed_changes:
			self.cmd = self.cmd_stash_list
			try:
				stashed = super().get_lines()
			except CommandError as e:
				log = self.format_command_error(e, setting='log-view.cmd.stash-list') + log
			else:
				if not stashed:
					pass
				elif self.stashed_changes_group or (self.stashed_changes_group is None and len(stashed) > 1):
					ln = formatter.format(title_stashes_group, number=len(stashed))
					ln = self.format_log_entry(settings.COLOR_LOG_STASHES, ln)
					log.insert(0, (ln, ID_STASHES_GROUP, TYPE_STASHED))
				else:
					log = self.format_stashed(stashed) + log

		return log

	status.arguments = ''
	status.description = _('Show stashed, untracked, unstaged and staged changes if existing')
	status.settings = [
		'log-view.show-untracked',
		'log-view.show-untracked-as-separate-group',
		'log-view.cmd.stash-list',
		'log-view.show-stashes',
		'log-view.show-stashes-as-group',
		'log-view.show-stashes-in-reverse-order',
		'log-view.line-pattern',
		'title.stashes',
		'title.untracked',
		'title.unstaged',
		'title.untracked-and-unstaged',
		'title.staged',
		settings.COLOR_LOG_STASHES,
		settings.COLOR_LOG_UNTRACKED,
		settings.COLOR_LOG_UNSTAGED,
		settings.COLOR_LOG_STAGED,
	]

	command_functions = dict(
		status = status,
	)

	def format_log_entry(self, color, logentry):
		ln = self.ln_pattern.format(logentry=logentry)
		ln = utils.colored_str_to_markup(ln, self.app.define_color)
		return (color, ln)

	def format_stashed(self, stashed):
		if self.stashed_changes_reversed_order:
			stashed = reversed(stashed)

		log = list()
		for ln in stashed:
			stash_id = self.extract_stash_id(ln)
			log.append((ln, stash_id, TYPE_STASHED))

		return log

	@classmethod
	def extract_hash_id(cls, text):
		m = cls.reo_hash_id.search(text)
		if m:
			return m.group(0)
		else:
			return None

	@classmethod
	def extract_stash_id(cls, text):
		m = cls.reo_stash_id.search(text)
		if m:
			return m.group(0)
		else:
			return None

class StashesModel(LogModel):

	def get_lines(self):
		self.cmd = self.cmd_stash_list
		try:
			stashed = Model.get_lines(self)
		except CommandError as e:
			return self.format_command_error(e, setting='log-view.cmd.stash-list')

		return self.format_stashed(stashed)

class UnreachableModel(LogModel):

	@classmethod
	def append_cmd_unreachable(cls, options):
		cls._append_cmd(cls.cmd_unreachable, options)

	def get_lines(self):
		self.cmd = self.cmd_unreachable
		try:
			lines = Model.get_lines(self)
		except CommandError as e:
			ln = self.ln_pattern_error.format(err=e.err, cmd=e.cmd)
			ln = utils.colored_str_to_markup(ln, self.app.define_color)
			return [(ln, None, TYPE_ERROR)]

		lines = [ln.split() for ln in lines]
		lines = [ln[2] for ln in lines if ln[0] == "unreachable" and ln[1] == "commit"]
		if not lines:
			err = error_no_unreachable_commits + "\n"
			ln = self.ln_pattern_error.format(err=err, cmd=self.cmd)
			ln = utils.colored_str_to_markup(ln, self.app.define_color)
			return [(ln, None, TYPE_ERROR)]

		original_cmd_log = self.cmd_log
		if self.are_several_commands(self.cmd_log):
			self.cmd_log = self._copy_command(self.cmd_log[-1])
		else:
			self.cmd_log = self._copy_command(self.cmd_log)
		self.append_cmd_log.__func__(self, ["--no-walk"])
		self.cmd_log += lines
		log = LogModel.get_lines(self)
		self.cmd_log = original_cmd_log
		return log


class DetailsModel(Model):

	WC_HASH_ID = settings.WC_HASH_ID

	cmd_pattern = [
		#["git", "show", "--color", "--decorate", "--no-patch", WC_HASH_ID],
		["$commitheader", WC_HASH_ID],
		["$referencedby", WC_HASH_ID],
		["git", "show", "--color", "--decorate", "--format=format:", "--patch", WC_HASH_ID],
	]
	cmd_start_header_data = ["git", "show"]
	cmd_pattern_tag = ["git", "show", "--color", "--format=%ncommit %H%n%cd", "--no-patch", WC_HASH_ID, "--"]
	cmd_pattern_blob = ["git", "show", WC_HASH_ID]
	cmd_pattern_tree = ["git", "show", "--color", WC_HASH_ID]
	cmd_unstaged = ["git", "diff", "--color"]
	cmd_staged = cmd_unstaged + ["--cached"]
	cmd_untracked = ["$untracked"]
	cmd_pattern_stashed = [
			["git", "log", "-g", "-1", "--pretty=format:%C(yellow)%gD%Creset%ncommit %H%nAuthor: %an <%ae>%nDate:   %ad%w(,4,4)%n%+B%n%n", "--color", WC_HASH_ID],
			["git", "stash", "show", "--patch", "--color", WC_HASH_ID],
	]
	cmd_referencing_commits = [w for w in LogModel.cmd_log[-1] if w != "--graph"] + ["--branches"]

	log_format_options = (
		'--no-decorate',
		'--decorate',
		'--decorate-refs',
		'--decorate-refs-exclude',
		'--use-mailmap',

		'--date-order',
		'--author-date-order',
		'--topo-order',
		'--reverse',

		'--pretty',
		'--format',
		'--abbrev-commit',
		'--no-abbrev-commit',
		'--oneline',
		'--encoding',

		'--expand-tabs',
		'--no-expand-tabs',

		'--notes',
		'--no-notes',

		'--show-signature',

		'--relative-date',
		'--date',

		'--left-right',
	)

	_diff_commands = ['cmd_pattern', 'cmd_unstaged', 'cmd_staged', 'cmd_pattern_stashed', 'cmd_start_header_data']


	@classmethod
	def append_cmd_diff(cls, options):
		for cmd in cls._diff_commands:
			cmd = getattr(cls, cmd)
			cls._append_cmd(cmd, options)

	@classmethod
	def remove_cmd_diff(cls, options):
		for cmd in cls._diff_commands:
			cmd = getattr(cls, cmd)
			cls._remove_cmd(cmd, options)

	@classmethod
	def toggle_cmd_diff(cls, options):
		sum_added = 0
		sum_removed = 0
		for cmd in cls._diff_commands:
			cmd = getattr(cls, cmd)
			added, removed = cls._toggle_cmd(cmd, options)
			sum_added += added
			sum_removed += removed

		return sum_added, sum_removed


	@classmethod
	def append_cmd_log(cls, options):
		for opt in options:
			# values are given in the same argument, separated by a =
			key = opt.split('=',1)[0]
			if key in cls.log_format_options:
				cls.cmd_referencing_commits.append(opt)

	@classmethod
	def remove_cmd_log(cls, options):
		cls._remove_cmd(cls.cmd_referencing_commits, options)

	@classmethod
	def toggle_cmd_log(cls, options):
		return cls._toggle_cmd(cls.cmd_referencing_commits, options)


	def remove_align_character(self):
		self.insert_align_character = False
		self.fmt_log = LogModel.fmt_log.replace(ALIGN_CHAR, "", 1)
		self.cmd_referencing_commits = self.replace_characters_in_cmd(type(self).cmd_referencing_commits, ALIGN_CHAR, "", 1)

	def restore_align_character(self):
		self.insert_align_character = True
		self.fmt_log = LogModel.fmt_log
		self.cmd_referencing_commits = type(self).cmd_referencing_commits


	decoration_head_branch_sep = " -> "

	ln_pattern_referencedby = "* {logentry}"
	ln_pattern_untracked_in_unstaged_changes = _("untracked:<color=default> {filename}</color>")
	ln_pattern_untracked_in_separate_group = _("{filename}")

	pattern_user = _("{name} <{email}>")

	linenumber_new = "{new}"
	linenumber_old = "{old}"
	linenumber_old_right = "{oldright}"
	linenumber_old_left = "{oldleft}"
	linenumber_sep = " "
	linenumber_off = ""
	linenumber_suffix = " "
	linenumber = linenumber_new
	min_line_number_width = 3

	re_ansi_esscape_sequence = "(\[[0-9;]*m)?"
	reo_start_new_file = re.compile(re_ansi_esscape_sequence + "diff (--git a/(?P<fn1>.*?) b/|--cc (?P<fn2>[^]*)|--combined (?P<fn3>[^]*))")
	reo_object_id = re.compile(re_ansi_esscape_sequence + "index ((?P<beforeleft>[0-9a-f]+),)?(?P<before>[0-9a-f]+)\.\.(?P<after>[0-9a-f]+)")
	reo_linenumber = re.compile(re_ansi_esscape_sequence +
		r"(@@@ -(?P<start_before_left>\d+)(,(?P<number_before_left>\d+))? -(?P<start_before_right>\d+)(,(?P<number_before_right>\d+))?"
		r"|@@ -(?P<start_before>\d+)(,(?P<number_before>\d+))?) "
		r"\+(?P<start_after>\d+)(,(?P<number_after>\d+))? @@"
	)
	reo_normal_line_exists_after = re.compile(re_ansi_esscape_sequence + r"[+ ]")
	reo_normal_line_existed_before = re.compile(re_ansi_esscape_sequence + r"[- ]")
	reo_merge_line_exists_after = re.compile(re_ansi_esscape_sequence + r"[+ ][+ ]")
	reo_merge_line_existed_left = re.compile(re_ansi_esscape_sequence  + r"([- ][+ ]|--)")
	reo_merge_line_existed_right = re.compile(re_ansi_esscape_sequence + r"([+ ][- ]|--)")

	reo_hash_id = LogModel.reo_hash_id
	reo_url = re.compile(r'\S+?([.]\S+)+')

	untracked_relative = settings.RELATIVE_CWD

	# if linenumbers are activated: insert ALIGN_CHAR in every line which is not represented by a tuple
	insert_align_character = True

	# if insert_align_character is activated: auto_move_align_character for lines in diff (not commit message)
	indent_broken_code = False

	def __init__(self, hash_id, id_type):
		self.hash_id = hash_id
		self.id_type = id_type
		self.is_merge = None
		self.is_diff = True

	def set_cmd(self):
		self.setting_cmd = None
		if self.hash_id == ID_STAGED:
			self.cmd = self.cmd_staged
			self.setting_cmd = 'details-view.cmd.staged'
			self.title = [(settings.COLOR_TITLE, title_staged)]
		elif self.hash_id == ID_UNSTAGED:
			self.cmd = self.cmd_unstaged
			self.setting_cmd = 'details-view.cmd.unstaged'
			self.title = [(settings.COLOR_TITLE, title_unstaged)]
			self.show_untracked_in_unstaged = LogModel.show_untracked and not LogModel.untracked_files_as_separate_group
		elif self.hash_id == ID_UNTRACKED:
			self.cmd = self.cmd_untracked
			self.setting_cmd = 'details-view.cmd.untracked'
			self.title = [(settings.COLOR_TITLE, title_untracked)]
		elif self.id_type == TYPE_STASHED:
			self.cmd = self.replace_in_cmd(self.cmd_pattern_stashed, self.WC_HASH_ID, self.hash_id)
			self.setting_cmd = 'details-view.cmd.stash'
			self.title = None
		else:
			try:
				self.object_type = get_object_type(self.hash_id)
			except CommandError as e:
				self.out.extend(self.format_command_error(e, _("get the object type")))
				self.object_type = None
			if self.object_type == OBJECT_TYPE_TAG:
				self.cmd = self.replace_in_cmd(self.cmd_pattern_tag, self.WC_HASH_ID, self.hash_id)
				self.setting_cmd = 'details-view.cmd.tag'
				self.title = None
				self.is_diff = False
			elif self.object_type == OBJECT_TYPE_TREE:
				self.cmd = self.replace_in_cmd(self.cmd_pattern_tree, self.WC_HASH_ID, self.hash_id)
				self.setting_cmd = 'details-view.cmd.tree'
				self.title = None
				self.is_diff = False
			elif self.object_type == OBJECT_TYPE_BLOB:
				self.cmd = self.replace_in_cmd(self.cmd_pattern_blob, self.WC_HASH_ID, self.hash_id)
				self.setting_cmd = 'details-view.cmd.blob'
				self.title = None
				self.is_diff = False
			else: # OBJECT_TYPE_COMMIT
				self.cmd = self.replace_in_cmd(self.cmd_pattern, self.WC_HASH_ID, self.hash_id)
				self.setting_cmd = 'details-view.cmd.commit'
				self.title = None

	def get_lines(self):
		"""
		returns a list of lines where each line is one of the following:
		- "text"
		- [("attr", "text")]  # urwid markup, must not contain tabs!
		- ("text", type)
		- ("text", type, auto_move_align_character)
		- ("text", TYPE_UNTRACKED, file_name)
		- ("text", TYPE_START_OF_FILE, file_info)
		- ("text", TYPE_NUMBERED_LINE, auto_move_align_character, line_info)
		"""
		self.object_type = None
		self.out = []
		self.set_cmd()
		out = self.out

		try:
			out.extend(super().get_lines())
		except CommandError as e:
			out.extend(self.format_command_error(e, setting=self.setting_cmd))
			return out

		if self.hash_id == ID_UNSTAGED and self.show_untracked_in_unstaged:
			cmd = self.cmd
			self.cmd = self.cmd_untracked
			try:
				untracked = super().get_lines()
			except CommandError as e:
				untracked = self.format_command_error(e, setting='details-view.cmd.untracked')
			else:
				pattern = self.ln_pattern_untracked_in_unstaged_changes
				untracked = self.format_untracked(pattern, untracked)
			finally:
				self.cmd = cmd

			if untracked:
				untracked.append("")
				out = untracked + out
				self.title = [(settings.COLOR_TITLE, title_unstaged_and_untracked)]
		elif self.hash_id == ID_UNTRACKED:
			pattern = self.ln_pattern_untracked_in_separate_group
			out = self.format_untracked(pattern, out)

		if self.is_diff:
			self.insert_linenumbers(out)

		if self.title:
			out.insert(0, self.title)
			out.insert(1, "")

		return out

	def format_untracked(self, pattern, filenames):
		path = lambda x: x
		if self.cmd_untracked == ['$untracked']:
			if self.untracked_relative == settings.RELATIVE_CWD:
				path = os.path.abspath
		return [([(settings.COLOR_DETAILS_UNTRACKED, utils.colored_str_to_markup(formatter.format(pattern, filename=fn), self.app.define_color))], TYPE_UNTRACKED, FileInfo(path(fn))) for fn in filenames]

	def format_command_error(self, e, action=None, setting=None):
		cmd = "cmd = %r\n" % (e.cmd,)
		err = e.err
		if action:
			err += "\n" + _("while trying to {do_action}").format(do_action=action)
		if setting:
			err += "\n" + _("see %{setting}%").format(setting=setting)

		return [cmd, (err, TYPE_ERROR)]

	def insert_linenumbers(self, out):
		self.file_info = None
		ns = NameSpace()
		ns.out = out
		ns.look_for_hint = True
		for ns.i in range(len(ns.out)):
			ln = ns.out[ns.i]
			if isinstance(ln, tuple):
				ns.i += 1
			elif isinstance(ln, list):
				ns.i += 1
			elif ns.look_for_hint:
				self.insert_linenumbers__process_metainfo_line(ns)
			else:
				self.insert_linenumbers__process_content_line(ns)

	def insert_linenumbers__process_metainfo_line(self, ns):
		ns.line_info = None
		ln = ns.out[ns.i]
		m = self.reo_linenumber.match(ln)
		if m:
			if m.group('start_before') is not None:
				self.is_merge = False
				self._set_linenumber(ns, 'before_right', m, 'before')
				ns.linenumber_before_left = ns.linenumber_before_right
				ns.last_linenumber_before_left = ns.last_linenumber_before_right
				ns.fmt_linenumber_before_left = ns.fmt_linenumber_before_right

				ns.reo_line_exists_after = self.reo_normal_line_exists_after
				ns.reo_line_existed_left = self.reo_normal_line_existed_before
				ns.reo_line_existed_right = self.reo_normal_line_existed_before
				ns.i_align_character = 1
			else:
				self.is_merge = True
				self._set_linenumber(ns, 'before_right', m, 'before_right')
				self._set_linenumber(ns, 'before_left', m, 'before_left')

				ns.reo_line_exists_after = self.reo_merge_line_exists_after
				ns.reo_line_existed_left = self.reo_merge_line_existed_left
				ns.reo_line_existed_right = self.reo_merge_line_existed_right
				ns.i_align_character = 2

			self._set_linenumber(ns, 'after', m, 'after')

			ns.look_for_hint = False
		else:
			m = self.reo_object_id.match(ln)
			if m:
				self.file_info.object_id_before_left = m.group('beforeleft')
				self.file_info.object_id_before_right = m.group('before')
				self.file_info.object_id_after = m.group('after')


		if self.insert_align_character:
			ns.out[ns.i] = ALIGN_CHAR + ln
		if self.is_start_new_file(ln):
			ns.out[ns.i] = (ns.out[ns.i], TYPE_START_OF_FILE, self.file_info)

	def _set_linenumber(self, ns, ns_name, match, re_name):
		linenumber = match.group('start_'+re_name)
		linenumber = int(linenumber)
		number_lines = match.group('number_'+re_name)
		if number_lines is None:
			last_linenumber = linenumber
		else:
			last_linenumber = linenumber + int(number_lines) - 1
		fmt = self.create_number_format(last_linenumber)
		setattr(ns, 'linenumber_'+ns_name, linenumber)
		setattr(ns, 'last_linenumber_'+ns_name, last_linenumber)
		setattr(ns, 'fmt_linenumber_'+ns_name, fmt)

	def create_number_format(self, last_linenumber):
		width = len(str(last_linenumber))
		width = max(width, self.min_line_number_width)
		return "%" + str(width) + "s"

	def insert_linenumbers__process_content_line(self, ns):
		orig_ln = ns.out[ns.i]
		ln = orig_ln

		if self.insert_align_character:
			ln = self.insert_align_char(ln, ns.i_align_character)

		ns.line_info = LineInfo()
		ln = (ln, TYPE_NUMBERED_LINE, self.indent_broken_code, ns.line_info)
		ns.out[ns.i] = ln

		self.increment_line_number_and_set_line_info(orig_ln, ns)

	def increment_line_number_and_set_line_info(self, orig_ln, ns):
		ns.line_info.linenumber_after = ns.linenumber_after
		ns.line_info.linenumber_before_right = ns.linenumber_before_right
		ns.line_info.linenumber_before_left = ns.linenumber_before_left
		ns.line_info.is_modified = False
		no_increment = True

		if ns.reo_line_exists_after.match(orig_ln):
			ns.line_info.formatted_linenumber_after = ns.fmt_linenumber_after % ns.linenumber_after
			ns.linenumber_after += 1
			no_increment = False
		else:
			ns.line_info.formatted_linenumber_after = ns.fmt_linenumber_after % ""
			ns.line_info.is_modified = True

		if ns.reo_line_existed_left.match(orig_ln):
			ns.line_info.formatted_linenumber_before_left = ns.fmt_linenumber_before_left % ns.linenumber_before_left
			ns.linenumber_before_left += 1
			no_increment = False
		else:
			ns.line_info.formatted_linenumber_before_left = ns.fmt_linenumber_before_left % ""
			ns.line_info.is_modified = True

		if ns.reo_line_existed_right.match(orig_ln):
			ns.line_info.formatted_linenumber_before_right = ns.fmt_linenumber_before_right % ns.linenumber_before_right
			ns.linenumber_before_right += 1
			no_increment = False
		else:
			ns.line_info.formatted_linenumber_before_right = ns.fmt_linenumber_before_right % ""
			ns.line_info.is_modified = True

		if no_increment:
			# The usual way of counting lines does not work.
			# This happens with --word-diff.
			# So I'm assuming each line is present in all versions.
			# Of course this is not always fullfilled.
			# But it's still better than giving each line the same number.
			ns.line_info.formatted_linenumber_after = ""
			ns.line_info.formatted_linenumber_before_left = ""
			ns.line_info.formatted_linenumber_before_right = ""
			ns.linenumber_after += 1
			ns.linenumber_before_left += 1
			ns.linenumber_before_right += 1

		if ns.linenumber_after > ns.last_linenumber_after and ns.linenumber_before_right > ns.last_linenumber_before_right and ns.linenumber_before_left > ns.last_linenumber_before_left:
			ns.look_for_hint = True

	@staticmethod
	def insert_align_char(ln, pos_align_character):
		n_escape = 0
		for m in ColorDecoder.reo_color_code.finditer(ln):
			i = m.start()
			pos = i - n_escape
			if pos >= pos_align_character:
				break
			n_escape += m.end() - i

		i_align_character = pos_align_character + n_escape
		return ln[:i_align_character] + ALIGN_CHAR + ln[i_align_character:]

	def is_start_new_file(self, ln):
		"""ln: str, possibly starting with one ansi escape sequence"""
		if isinstance(ln, list):
			return False
		m = self.reo_start_new_file.match(ln)
		if m:
			fn = m.group('fn1')
			if fn is None:
				fn = m.group('fn2')
				if fn is None:
					fn = m.group('fn3')
			self.file_info = FileInfo()
			self.file_info.fn = fn
			return True
		else:
			return False


	# ------- command functions ------

	def referencedby(self, args):
		assert len(args) == 1
		hash_id = args[0]

		cmd = ["git", "show", "--format=%h", "--no-patch", hash_id]
		short_hash = self.run_and_get_output(cmd).strip()

		bak = self.cmd
		self.cmd = self.cmd_referencing_commits +  ["--grep", r"\<"+short_hash]
		self.cmd = self.replace_custom_format(self.cmd)
		try:
			out = super().get_lines()
		except CommandError as e:
			msg = "command for searching referencing commits failed:\ncmd = {e.cmd}\n{e.err}\nreturn code: {e.returncode}".format(e=e)
			return [(msg, TYPE_ERROR)]
		self.cmd = bak

		out = [(self.ln_pattern_referencedby.format(logentry=ln), TYPE_OTHER) for ln in out]
		if out:
			out.insert(0, title_referencedby)
			out.insert(0, "")

		return out

	referencedby.arguments = 'CURRENT_COMMIT_HASH'
	referencedby.description = _('Show a list of commits referencing the current commit')
	referencedby.settings = ['details-view.cmd.commit.referenced-by', 'details-view.commit.line-pattern-referenced-by']

	def untracked(self, args):
		assert len(args) == 0

		self.cmd = ["git", "status", "--porcelain=v1"]
		status = super().get_lines()
		root = get_git_root()

		files = []

		# X: index
		# Y: work tree
		for ln in status:
			if ln[:2] == '??':
				fn = ln[3:]
				if self.untracked_relative == settings.RELATIVE_ROOT or self.untracked_relative == settings.RELATIVE_CWD:
					fn = os.path.join(root, fn)
					if self.untracked_relative == settings.RELATIVE_CWD:
						fn = os.path.relpath(fn)
				files.append(fn)

		return files

	untracked.arguments = ''
	untracked.description = _('Return untracked files')
	untracked.settings = ['details-view.show-untracked-relative-to']

	indent_body = _("    ")
	def commitheader(self, args):
		assert len(args) == 1
		hash_id = args[0]

		out = []
		values = self.get_commit_header_data(hash_id)
		if values is None:
			return []
		refnames = values.pop('refnames')
		if refnames:
			markup_refnames = utils.replace_to_markup(refnames, ', ', refnames_sep, markup_function=self.markup_deco)
			markup_refnames = utils.replace_to_markup(pattern_refnames, '{refnames}', markup_refnames)
		else:
			markup_refnames = ""

		title = title_commit.format(refnames='{refnames}', **values)
		markup_title = utils.replace_to_markup(title, '{refnames}', markup_refnames)
		markup_title = [(settings.COLOR_TITLE, markup_title)]
		out.append(markup_title)
		self.append_author_committer(out, values)
		out.append("")
		out.append(self.indent_body + values["subject"])
		body = values["body"].rstrip()
		if body:
			out.append("")
			out.append(self.indent_body + body)
		return out

	def get_commit_header_data(self, hash_id):
		key_fmt = ">>> %s:"
		keys = (
			("hash_id", "%H"),
			("refnames", "%D"),
			("subject", "%s"),
			("committer_name", "%cn",),
			("committer_email", "%ce",),
			("committer_date", "%cd",),
			("author_name", "%an",),
			("author_email", "%ae",),
			("author_date", "%ad",),
			("body", "%b"),
			("EOF", "") # ignore trailing newline while ensuring that body is added to values
		)
		fmt = "\n".join((key_fmt % key) + "\n" + wc for key,wc in keys)

		self.cmd = self.cmd_start_header_data + ["--no-patch", "--format="+fmt, hash_id]
		try:
			lines = super().get_lines()
		except CommandError as e:
			self.out.extend(self.format_command_error(e, setting='details-view.cmd.commit.header-data'))
			return None

		values = {}
		current_key = None
		next_key_index = 0
		for ln in lines:
			if next_key_index < len(keys) and ln == key_fmt % keys[next_key_index][0]:
				current_key = keys[next_key_index][0]
				next_key_index += 1
			else:
				if current_key not in values:
					values[current_key] = ln
				else:
					values[current_key] += "\n" + ln

		return values

	def append_author_committer(self, out, values):
		fmt = self.pattern_user
		author = fmt.format(name=values['author_name'], email=values['author_email'])
		committer = fmt.format(name=values['committer_name'], email=values['committer_email'])
		author_date = values['author_date']
		committer_date = values['committer_date']

		align_char = ALIGN_CHAR if self.insert_align_character else ""

		t = []
		if author == committer:
			t.append((_("Author/Committer"), align_char + author))
		else:
			t.append((_("Author"), align_char + author))

		if author_date != committer_date:
			t.append((_("Author Date"), align_char + author_date))

		if committer != author:
			t.append((_("Committer"), align_char + committer))

		if committer_date == author_date:
			t.append((_("Date"), align_char + author_date))
		else:
			t.append((_("Committer Date"), align_char + committer_date))

		for ln in utils.format_table(t, fmt=['%s:']):
			ln = utils.colored_str_to_markup(ln, define_color=self.app.define_color)
			# wrap line in a tuple so that ALIGN_CHAR is not added again
			ln = (ln, None)
			out.append(ln)

	def markup_deco(self, decoration):
		HEAD_SEP = " -> "
		i = decoration.find(HEAD_SEP)
		if i >= 0:
			head = decoration[:i]
			sep = self.decoration_head_branch_sep
			i += len(HEAD_SEP)
			branch = decoration[i:]
			return [(settings.COLOR_DECORATION_HEAD, head), (settings.COLOR_DECORATION_HEAD_BRANCH_SEP, sep), (settings.COLOR_DECORATION_BRANCH_LOCAL, branch)]

		if decoration.startswith("tag: "):
			return (settings.COLOR_DECORATION_TAG, decoration)

		if decoration in self.get_local_branches():
			return (settings.COLOR_DECORATION_BRANCH_LOCAL, decoration)

		if decoration in self.get_remote_branches():
			return (settings.COLOR_DECORATION_BRANCH_REMOTE, decoration)

		return decoration

	commitheader.arguments = 'CURRENT_COMMIT_HASH'
	commitheader.description = _('Show the meta info of the current commit (hash, branch, tag, author, committer, date, message)')
	commitheader.settings = [
		'details-view.cmd.commit.header-data',
		'details-view.commit.user-pattern',
		'title.commit.refnames.head-branch-sep',
		settings.COLOR_TITLE,
		settings.COLOR_DECORATION_HEAD,
		settings.COLOR_DECORATION_HEAD_BRANCH_SEP,
		settings.COLOR_DECORATION_BRANCH_LOCAL,
		settings.COLOR_DECORATION_BRANCH_REMOTE,
		settings.COLOR_DECORATION_TAG,
	]


	command_functions = dict(
		referencedby = referencedby,
		untracked = untracked,
		commitheader = commitheader,
	)


class DiffModel(DetailsModel):

	cmd = ['git', 'diff', '--color']

	_diff_commands = ['cmd']

	def __init__(self, args):
		self.hash_id = None
		self.id_type = None
		self.title = None

		self.args = args
		self.is_diff = True

		self.is_merge = None

	def set_cmd(self):
		self.setting_cmd = "details-view.cmd.diff"
		self.cmd = type(self).cmd + self.args



# ---------- modifiers ----------

def append_cmd_log(log_args):
	LogModel.append_cmd_log(log_args)
	DetailsModel.append_cmd_log(log_args)

def remove_cmd_log(log_args):
	LogModel.remove_cmd_log(log_args)
	DetailsModel.remove_cmd_log(log_args)

def toggle_cmd_log(log_args):
	sum_added = 0
	sum_removed = 0
	for cls in (LogModel, DetailsModel):
		added, removed = cls.toggle_cmd_log(log_args)
		sum_added += added
		sum_removed += removed

	return sum_added, sum_removed


def append_cmd_unreachable(unreachable_args):
	UnreachableModel.append_cmd_unreachable(unreachable_args)


def append_cmd_diff(diff_args):
	DetailsModel.append_cmd_diff(diff_args)
	DiffModel.append_cmd_diff(diff_args)

def remove_cmd_diff(diff_args):
	DetailsModel.remove_cmd_diff(diff_args)
	DiffModel.remove_cmd_diff(diff_args)

def toggle_cmd_diff(log_args):
	sum_added = 0
	sum_removed = 0
	for cls in (DetailsModel, DiffModel):
		added, removed = cls.toggle_cmd_diff(log_args)
		sum_added += added
		sum_removed += removed

	return sum_added, sum_removed


# ---------- getters ----------

def get_containing_tag(hash_id, exclusive):
	cmd = ["git", "tag", "--list", "--contains", hash_id, "--sort", "version:refname"]
	out = Runner().run_and_get_output(cmd)
	out = out.rstrip()
	out = out.splitlines()
	if exclusive:
		for tag in out:
			if is_same_commit(tag, hash_id):
				continue
			return tag
		return None

	if out:
		return out[0]
	else:
		return None

def get_last_tag(hash_id, exclusive):
	if exclusive:
		hash_id = "%s^" % hash_id
	cmd = ["git", "describe", "--abbrev=0", hash_id]
	try:
		out = Runner().run_and_get_output(cmd)
	except CommandError:
		return None

	out = out.rstrip()
	return out

def is_same_commit(rev1, rev2):
	return get_commit_hash(rev1) == get_commit_hash(rev2)

def get_commit_hash(revision):
	# show does not work because it shows the annotation for tags
	cmd = ["git", "log", "-1", "--pretty=format:%H", revision, "--"]
	out = Runner().run_and_get_output(cmd)
	out = out.rstrip()
	return out

def get_object_type(hash_id):
	cmd = ["git", "cat-file", "-t", hash_id]
	out = Runner().run_and_get_output(cmd)
	out = out.rstrip()
	return out

def get_git_version():
	cmd = ["git", "--version"]
	try:
		out = Runner().run_and_get_output(cmd)
	except CommandError:
		return None

	out = out.rstrip()
	return out

def get_git_root():
	cmd = ["git", "rev-parse", "--show-toplevel"]
	try:
		out = Runner().run_and_get_output(cmd)
	except CommandError:
		return None

	out = out.rstrip()
	return out

def get_relative_path(path):
	'''
	path: a path relative to the git root directory
	returns: a path relative to the current working directory
	'''
	if os.path.isabs(path):
		return path
	root = get_git_root()
	cwd = os.getcwd()
	cwd = os.path.relpath(cwd, root) + os.sep
	return os.path.relpath(path, cwd)


# ---------- opener ----------

def initattr(obj, name, value):
	if hasattr(obj, name):
		return
	setattr(obj, name, value)

class Opener:

	def __init__(self):
		settings
		self._map = {}
		self.add_editor("vi", linenumber="+{ln}", readonly="-R")
		self.add_editor("vim", linenumber="+{ln}", readonly="-R")
		self.add_editor("nano", linenumber="+{ln}", readonly="-v")

	def add_editor(self, name, command=None, *, linenumber="", readonly=""):
		if not command:
			command = name
		self._map[command] = name
		setattr(self,  "editor_%s_command" % name, command)
		initattr(self, "editor_%s_linenumber" % name, linenumber)
		initattr(self, "editor_%s_readonly" % name, readonly)
		settings.settings["editor.%s.command" % name] = ("app.model.opener.editor_%s_command" % name, str, _("the value of the EDITOR environment variable which activates the corresponding editor settings"))
		settings.settings["editor.%s.linenumber" % name] = ("app.model.opener.editor_%s_linenumber" % name, str, _("a command line argument which is added if a specific line shall be selected, the wild card {ln} specifies the line number"))
		settings.settings["editor.%s.readonly" % name] = ("app.model.opener.editor_%s_readonly" % name, str, _("a command line argument which is added if a file shall be opened read only"))

	def get_editor(self):
		cmd = os.environ.get('EDITOR', None)
		if cmd:
			name = self._map.get(cmd, None)
			if name is None:
				# in case EDITOR is an absolute path
				name = self._map.get(os.path.split(cmd)[1], None)
		else:
			name = "vi"
			cmd = self.get_editor_argument(name, "command")
			assert cmd
		return name, cmd

	def get_editor_argument(self, editor_name, argument_name):
		return getattr(self, "editor_%s_%s" % (editor_name, argument_name), "")

	def open_old_version_in_editor(self, fn, commit, object_id, which, line_number):
		fn = os.path.split(fn)[1]
		basename,ext = os.path.splitext(fn)
		tmpfn = "{fn}@{which}-{commit}{ext}".format(fn=basename, which=which, commit=commit, ext=ext)
		runner = Runner()
		with tempfile.TemporaryDirectory() as tmpdir:
			tmpfn = os.path.join(tmpdir, tmpfn)
			with open(tmpfn, 'wt') as f:
				cmd = ['git', 'show', object_id]
				content = runner.run_and_get_output(cmd)
				f.write(content)
			os.chmod(tmpfn, stat.S_IREAD)
			self.open_file_in_editor(f.name, line_number, read_only=True)

	def open_file_in_editor(self, fn, line_number, read_only=False, create_dirs=False):
		if not os.path.exists(fn):
			if create_dirs:
				path = os.path.split(os.path.abspath(fn))[0]
				os.makedirs(path, exist_ok=True)
			else:
				raise FileNotFoundError(fn)
		if line_number == 0:
			line_number = 1
		runner = Runner()
		editor_name, cmd = self.get_editor()
		if line_number is not None:
			cmd += " " + self.get_editor_argument(editor_name, "linenumber").format(ln=line_number)
		if read_only:
			cmd += " " + self.get_editor_argument(editor_name, "readonly")
		cmd += " " + shlex.quote(fn)
		runner.run_interactive(cmd, shell=True)

	def check_editor(self):
		editor_name, cmd = self.get_editor()
		exe = shlex.split(cmd)[0]
		which = shutil.which(exe)
		if not which:
			if editor_name is None:
				editor_name = _("<unknown editor>")
			return _("cannot open editor {editor_name}, no such executable {exe!r}").format(exe=exe, editor_name=editor_name)
	
		return None


opener = Opener()
open_old_version_in_editor = opener.open_old_version_in_editor
open_file_in_editor = opener.open_file_in_editor
check_editor = opener.check_editor


if __name__ == '__main__':
	log = LogModel()
	for ln in log.get_lines():
		print(ln)
