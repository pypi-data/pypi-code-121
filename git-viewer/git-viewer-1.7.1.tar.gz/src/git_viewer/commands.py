#!/usr/bin/env python3

import os
import re
import shlex
import gettext
_ = gettext.gettext

from . import api_commands as commands
from . import model
from . import settings
from . import utils
ErrorInCommand = commands.ErrorInCommand

LOG_LEVEL_CHOICES = [i[0] for i in settings.LOG_LEVELS]

# don't use app.show_error but raise ErrorInCommand
# so that additional information on the command can be added


class quit(commands.Command):

	"""
	Exit the application.
	"""

	run_before_init = False
	run_after_init = False

	def execute(self, args):
		self.app.quit()

class layout(commands.Command):

	"""
	Choose a different layout how to display the views.

	After choosing a layout which shows several views at once
	you can set their size using the command `resize`.
	"""

	@classmethod
	def init_parser(cls, parser):
		cls.modes = [
			(cls.app.VIEW_MODE_HOR, _("horizontal"), _("Show several views side by side")),
			(cls.app.VIEW_MODE_VER, _("vertical"), _("Show several views above each other")),
			(cls.app.VIEW_MODE_ONE, _("one"), _("Show only the currently focused view, as big as possible")),
			(cls.app.PSEUDO_VIEW_MODE_SPLIT, _("split"), _("Toggle between {hor} and {ver}").format(hor=cls.app.VIEW_MODE_HOR, ver=cls.app.VIEW_MODE_VER)),
			(cls.app.PSEUDO_VIEW_MODE_AUTO, _("auto"), _("Choose a layout depending on %layout.preferred%, %layout.required-width-for-hor% and %layout.required-height-for-ver%")),
		]
		parser.add_argument("mode", choices=[m[0] for m in cls.modes])

	@classmethod
	def init_help_lines(cls, parser):
		super().init_help_lines(parser)
		out = cls.help_lines

		out.append("")
		out.append(_("available layouts:"))
		modes = []
		for mode, long_name, helpstr in cls.modes:
			if long_name != mode:
				mode = _("{mode} ({long_name})").format(mode=mode, long_name=long_name)
			modes.append((mode, helpstr))

		mode_width = lambda m: len(m[0])
		maxwidth_mode = mode_width(max(modes, key=mode_width))
		fmt = "  {mode:%s}  ^{help}" % maxwidth_mode
		for mode, helpstr in modes:
			ln = fmt.format(mode=mode, help=helpstr)
			ln = cls.AlignedLine(ln)
			out.append(ln)

	def execute(self, args):
		mode = args.mode
		self.app.view(mode)

class go(commands.Command):

	"""
	Go to another view.
	Open it if it does not exist yet and make it visible.
	"""

	@classmethod
	def init_parser(cls, parser):
		modes = cls.app.go_map.keys()
		parser.add_argument("direction", choices=modes)
		parser.add_argument("--open-only", action="store_true", help="Open but without focusing it if it is visible")
		tag = parser.add_argument_group(_("tag options"))
		exclusive = tag.add_mutually_exclusive_group()
		exclusive.add_argument("--last", dest="containing", action="store_false", default=None, help=_("Open the latest tag existing at the current commit"))
		exclusive.add_argument("--containing", dest="containing", action="store_true", default=None, help=_("Open the next tag containing the current commit"))
		tag.add_argument("--toggle", action="store_true", default=None, help=_("Return to the last view if the tag is already opened"))

	@classmethod
	def init_help(cls, parser):
		super().init_help(parser)

		parser.description += "\n"
		parser.description += "\n"
		parser.description += "choices:\n"
		width = len(max(cls.app.go_map.keys(), key=len))
		direction_fmt = '  {to:%s}  {help}' % width
		direction_help = [
			direction_fmt.format(to=cls.app.GO_DETAILS, help=_("Open details")),
			direction_fmt.format(to=cls.app.GO_TAG, help=_("Open tag")),
			direction_fmt.format(to=cls.app.GO_LOG, help=_("Return to the first view")),
			direction_fmt.format(to=cls.app.GO_LEFT, help=_("Go to the previous view")),
			direction_fmt.format(to=cls.app.GO_RIGHT, help=_("Go to the next view")),
			direction_fmt.format(to=cls.app.GO_TOGGLE, help=_("If several views are visible toggle between them")),
		]
		parser.description += "\n".join(direction_help)

	def execute(self, args):
		direction = args.direction
		if direction != self.app.GO_TAG:
			if args.containing is not None:
				raise ErrorInCommand(_("--last and --containing can be used with tag only"))
			if args.toggle is not None:
				raise ErrorInCommand(_("--toggle can be used with tag only"))
			self.app.go(direction, open_only=args.open_only)
		else:
			self.app.go_tag(containing=args.containing, toggle=args.toggle, open_only=args.open_only)

class help(commands.Command):

	"""
	Show help.
	"""

	@classmethod
	def init_parser(cls, parser):
		group = parser.add_mutually_exclusive_group()
		group.add_argument("--introduction", action="store_true", help=_("Show a general help for this program"))
		group.add_argument("--shortcuts", action="store_true", help=_("Show a list of all defined keyboard shortcuts"))
		group.add_argument("--commands", action="store_true", help=_("Show a list of all available commands"))
		group.add_argument("--settings", action="store_true", help=_("Show a list of all available settings"))

		group.add_argument("-c", "--cmd", help=_("Show the help for the specified command"))

	def execute(self, args):
		if args.commands:
			self.app.show_available_commands()
		elif args.shortcuts:
			self.app.show_keyboard_shortcuts()
		elif args.settings:
			self.app.show_settings()
		elif args.cmd:
			self.app.show_help_for_command(args.cmd)
		else:
			self.app.show_introduction()

class linenumber(commands.Command):

	"""
	Configure line numbers in details view.
	"""

	run_before_init = True

	@classmethod
	def init_parser(cls, parser):
		cls.model = model.DetailsModel
		group = parser.add_mutually_exclusive_group()
		group.add_argument("--new", action='store_const', const=cls.model.linenumber_new, dest='_fmt', help=_("Show the line numbers after the commit"))
		group.add_argument("--old", action='store_const', const=cls.model.linenumber_old, dest='_fmt', help=_("Show the line numbers before the commit (in case of a combined diff: left and right version)"))
		group.add_argument("--old-left", action='store_const', const=cls.model.linenumber_old_left, dest='_fmt', help=_("Show the line numbers before the commit (in case of a combined diff: the left version)"))
		group.add_argument("--old-right", action='store_const', const=cls.model.linenumber_old_right, dest='_fmt', help=_("Show the line numbers before the commit (in case of a combined diff: the right version)"))
		group.add_argument("--toggle", action='store_true', help=_("Toggle between --old and --new"))
		group.add_argument("--off", action='store_const', const=cls.model.linenumber_off, dest='_fmt', help=_("Do not show line numbers"))

	def execute(self, args):
		if args.toggle:
			args.fmt = self.model.linenumber_new if self.model.linenumber==self.model.linenumber_old else self.model.linenumber_old
		else:
			args.fmt = args._fmt
		self.app.line_numbers(args.fmt)

class load(commands.Command):

	"""
	Load a configuration file.
	If no file name is specified check the default paths (see below) and load the first one existing.
	If the specified file is a relative path it is treated relative to the config file it appears in
	or relative to the current working directory if this command is used outside of a config file.

	Each line contains a call to one programmable command (see `help --commands`).
	Most interesting for a config file are the commands `set`, `map` and `unmap`.
	Empty lines and lines starting with "{commentchar}" are ignored.
	Not all programmable commands can be used in a config file.
	Whether a programmable command can be used in a config file
	is noted in the section "behavior in config file" of the command help.

	When git-viewer starts it automatically tries to load
	the first config file it can find in the default paths.
	Some commands need to be run before initialization so that
	they can change settings which are applied during initialization.
	Other commands need to be run after initialization because
	they depend on widgets which are created during initialization.
	Therefore, if a config file is found it is loaded twice at startup.
	Most error messages which have already occurred the first time
	are suppressed the second time in order to avoid duplicates.
	"""

	name = "config.load"

	run_before_init = True
	run_after_init = True

	@classmethod
	def init_parser(cls, parser):
		parser.add_argument('file', nargs='?')
		parser.add_argument('--default-path', action='store_true', help=_("Check the default paths even if git-viewer was started with --config, if file is given replace the filenames in the default paths with file"))
		parser.add_argument('-l', '--log-level', choices=LOG_LEVEL_CHOICES, default=settings.LOG_LEVEL_NAME_WARNING, help=_('Change %%app.log-level%% for loading this config file, defaults to %(default)s'))
		parser.add_argument('-i', '--ignore-missing', action='store_true', help=_("Don't print an error if file does not exist"))

	@classmethod
	def init_help_lines(cls, parser):
		cls.__doc__ = cls.__doc__.format(commentchar=cls.app.COMMENT)
		super().init_help_lines(parser)
		out = cls.help_lines

		out.append("")
		out.append(_("default config file paths:"))
		pattern = _("  %s")
		for fn in cls.app.get_config_files(only_existing=False):
			out.append(pattern % fn)

	def execute(self, args):
		log_level = self.app.log_level_name_to_value(args.log_level)
		self.app.load_config(args.file, default_path=args.default_path, ignore_missing_file=args.ignore_missing, log_level=log_level)

class config_export(commands.Command):

	"""
	Export all settings and keybindings to a file which can be imported with `config.load`.
	If no file name is specified write to the first default path.
	If the specified file is a relative path it is relative to the current working directory
	(except if this command is used inside of a config file, then it's relative to that file).

	The exported config file is not necessarily equivalent to a previously loaded config file.
	For example if the loaded config file uses the command `layout` this has no influence on exported settings.
	Instead you can change the setting %layout.preferred%.
	"""

	name = "config.export"

	run_before_init = False
	run_after_init = True

	@classmethod
	def init_parser(cls, parser):
		parser.add_argument('file', nargs='?')
		parser.add_argument('--default-path', action='store_true', help=_("Check the default paths even if git-viewer was started with --config, if file is given replace the filenames in the default paths with file"))

		parser.add_argument('-f', '--force', action='store_true', help=_("Overwrite existing file"))

		parser.add_argument('--settings', action='store_true', default=None, help=_("Export settings (`set`)"))
		parser.add_argument('--keybindings', action='store_true', default=None, help=_("Export keybindings (`map` and `map-fallback`)"))
		parser.add_argument('--no-help', action='store_true', help=_("Do not add comments"))
		parser.add_argument('--comment-out', action='store_true', help=_("Comment out all lines"))

	@classmethod
	def init_help_lines(cls, parser):
		cls.__doc__ = cls.__doc__.format(commentchar=cls.app.COMMENT)
		super().init_help_lines(parser)
		out = cls.help_lines

		out.append("")
		out.append(_("default config file paths:"))
		pattern = _("  %s")
		for fn in cls.app.get_config_files(only_existing=False):
			out.append(pattern % fn)

	def execute(self, args):
		if args.settings is None and args.keybindings is None:
			args.settings = True
			args.keybindings = True
		self.app.export_config(args.file, overwrite=args.force, settings=args.settings, keybindings=args.keybindings, default_path=args.default_path, comment_out=args.comment_out, export_help=not args.no_help)

class config_edit(commands.Command):

	"""
	Open the config file in an editor.
	If no file name is specified open the first existing file in the default paths or the first default path if no file is existing.
	If the specified file is a relative path it is relative to the current working directory.

	Load the config file after the editor is closed if %config.auto-reload% is enabled.
	"""

	name = "config.edit"

	run_before_init = False
	run_after_init = False

	@classmethod
	def init_parser(cls, parser):
		parser.add_argument('file', nargs='?')
		parser.add_argument('--default-path', action='store_true', help=_("Check the default paths even if git-viewer was started with --config, if file is given replace the filenames in the default paths with file"))
		parser.add_argument('-1', '--ignore-existing', action='store_true', help=_("Open the first default path independent of whether it or other files are existing"))

	@classmethod
	def init_help_lines(cls, parser):
		cls.__doc__ = cls.__doc__.format(commentchar=cls.app.COMMENT)
		super().init_help_lines(parser)
		out = cls.help_lines

		out.append("")
		out.append(_("default config file paths:"))
		pattern = _("  %s")
		for fn in cls.app.get_config_files(only_existing=False):
			out.append(pattern % fn)

	def execute(self, args):
		if args.file and args.ignore_existing:
			raise ErrorInCommand(_("--ignore-existing cannot be used when file is given"))

		self.app.open_config(args.file, ignore_existing=args.ignore_existing, default_path=args.default_path)

class open(commands.Command):

	"""
	Open the current file in a text editor.

	The text editor can be chosen via the environment variable EDITOR.
	vi, vim and nano are supported out of the box.
	If you want to use another editor take a look at `add-editor`.
	If EDITOR is not set vi is used.
	"""

	run_before_init = False
	run_after_init = False

	@classmethod
	def init_parser(cls, parser):
		group = parser.add_mutually_exclusive_group()
		group.add_argument("--after",  action='store_const', dest='version', const=cls.app.OPEN_AFTER,  help=_("Open the version of the current file after this commit (read only)"))
		group.add_argument("--before", action='store_const', dest='version', const=cls.app.OPEN_BEFORE_RIGHT, help=_("Open the version of the current file before this commit (in case of a combined diff: the right version) (read only)"))
		group.add_argument("--before-left", action='store_const', dest='version', const=cls.app.OPEN_BEFORE_LEFT, help=_("Open the version of the current file before this commit (in case of a combined diff: the left version) (read only)"))
		group.add_argument("--before-right", action='store_const', dest='version', const=cls.app.OPEN_BEFORE_RIGHT, help=_("Open the version of the current file before this commit (in case of a combined diff: the right version) (read only)"))
		group.add_argument("--now",    action='store_const', dest='version', const=cls.app.OPEN_NOW,    help=_("Open the current file in the working directory (writable)"))
		group.set_defaults(version=cls.app.OPEN_AFTER)

	def execute(self, args):
		self.app.open_external(which=args.version)

class option(commands.Command):

	"""
	Append or remove command line options for the git commands.
	If a command is a list of several commands the options
	are applied to the last command in that list only.
	You need to seperate the options that you want to apply to the git commands
	from the options of this command with a double hyphen.

	Line numbers are not available (too inacurate to be displayed) with --word-diff.

	examples:
	  option --log --remove -- --date=relative
	  option --diff --add -- --date=iso
	  option --diff --toggle -- --ignore-space-change
	  option --diff --toggle -- --word-diff=color
	"""

	run_before_init = True

	ACTION_ADD = 'add'
	ACTION_REMOVE = 'rm'
	ACTION_TOGGLE = 'toggle'

	@classmethod
	def init_parser(cls, parser):
		group = parser.add_mutually_exclusive_group()
		group.add_argument('--diff', action='store_true', dest='diff')
		group.add_argument('--log', action='store_false', dest='diff')
		group.set_defaults(diff=None)
		group = parser.add_mutually_exclusive_group()
		group.add_argument('--add', action='store_const', const=cls.ACTION_ADD, dest='action')
		group.add_argument('--remove', action='store_const', const=cls.ACTION_REMOVE, dest='action')
		group.add_argument('--toggle', action='store_const', const=cls.ACTION_TOGGLE, dest='action')
		group.set_defaults(action=cls.ACTION_ADD)
		parser.add_argument('options', nargs='+')
	
	def execute(self, args):
		if args.diff is None:
			raise ErrorInCommand(_("missing option --diff or --log"))
		elif args.diff:
			if args.action == self.ACTION_ADD:
				self.app.show_info(_("option --add --diff -- %s") % args.options)
				model.append_cmd_diff(args.options)
			elif args.action == self.ACTION_REMOVE:
				self.app.show_info(_("option --remove --diff -- %s") % args.options)
				model.remove_cmd_diff(args.options)
			elif args.action == self.ACTION_TOGGLE:
				added, removed = model.toggle_cmd_diff(args.options)
				self.show_result("diff", args.options, added, removed)
			else:
				assert False, 'invalid action %r' % (args.action,)
		else:
			if args.action == self.ACTION_ADD:
				self.app.show_info(_("option --add --log -- %s") % args.options)
				model.append_cmd_log(args.options)
			elif args.action == self.ACTION_REMOVE:
				self.app.show_info(_("option --remove --log -- %s") % args.options)
				model.remove_cmd_log(args.options)
			elif args.action == self.ACTION_TOGGLE:
				added, removed = model.toggle_cmd_log(args.options)
				self.show_result("log", args.options, added, removed)
			else:
				assert False, 'invalid action %r' % (args.action,)

		if self.app.is_auto_open_enabled:
			self.app.reload()
	
	def show_result(self, cmd, options, added, removed):
		msg = _("option --toggle --{cmd} -- {options} => ").format(cmd=cmd, options=options)
		if added == 0:
			if removed == 0:
				msg += _("ERROR: nothing seems to have changed but that should not be the case. Please file a bug report.")
			else:
				msg += _("removed")
		else:
			if removed == 0:
				msg += _("added")
			else:
				msg += _("some added, some removed")
		self.app.show_info(msg)


class reload(commands.Command):

	"""
	Reload the current view.

	Please note that commits are immutable.
	If you amend a commit a new commit is created
	but reloading a details view will still display the old commit.

	A details view can change on reload if
	- it shows staged or unstaged changes and changes have been added, reset or committed
	- it shows a stash and changes have been stashed or stashes have been dropped
	- a new commit is committed which references the currently displayed commit
	- settings have changed
	"""

	@classmethod
	def init_parser(cls, parser):
		parser.add_argument('--all', action='store_false', dest='only_current', help=
			"Reload the current view and all views left of it. "
			"Discard all views right of the current view. "
			"Automatically reopen if %%details-view.auto-open%% is enabled.")

	def execute(self, args):
		self.app.reload(args.only_current)

class search(commands.Command):

	"""
	Search for a text.
	"""

	run_before_init = False
	run_after_init = False

	CMD_OPEN = "open"
	CMD_NEXT = "next"
	CMD_PREV = "prev"
	CMD_EDIT = "edit"

	@classmethod
	def init_parser(cls, parser):
		group = parser.add_mutually_exclusive_group()
		group.add_argument("--open", dest="cmd", action="store_const", const=cls.CMD_OPEN, default=cls.CMD_NEXT, help=_("Open a text box to enter the search text"))
		group.add_argument("--next", dest="cmd", action="store_const", const=cls.CMD_NEXT, help=_("Go to the next match"))
		group.add_argument("--prev", dest="cmd", action="store_const", const=cls.CMD_PREV, help=_("Go to the previous match"))
		group.add_argument("--edit", dest="cmd", action="store_const", const=cls.CMD_EDIT, help=_("Open the text box to change the current search text"))

		group = parser.add_argument_group(_("arguments for --open"))
		group.add_argument("--reverse", action="store_true", help=_("Search in reversed direction"))

		#TODO
		#parser.add_argument("searchtext", nargs='?', help=("The text to search for."))

	@classmethod
	def init_help(cls, parser):
		super().init_help(parser)
		description = []

		settings = {
			'case_sensitive' : {
				True : _("Case sensitive"),
				False : _("Case insensitive"),
				None : _("Auto case sensitivity (case sensitive if search text contains upper case characters, case insensitive otherwise)"),
			},
			'is_regex' : {
				True : _("Regular expression"),
				False : _("Literal string"),
			},
		}

		def get_text(key, val):
			values = settings.get(key)
			if values:
				text = values.get(val)
				if text:
					return text

			text = "{key} = {val}".format(key=key, val=val)
			return text

		li_pattern = _("- {}")
		description.append(_("search flags:"))
		description.append(_("The search text can be followed by flags which change the search settings for this search."))
		description.append(_("The search flags are separated by a {flag_sep}.").format(flag_sep=cls.app.SearchEdit.FLAG_SEP))
		description.append(_("If the search text contains a {flag_sep} it must be terminated by a {flag_sep} even if no flags are given.").format(flag_sep=cls.app.SearchEdit.FLAG_SEP))
		description.append(_("The following search flags are available:"))
		flag_pattern = li_pattern.format(_("{flag}: {descr}"))
		for flag, (key, val) in sorted(cls.app.SearchEdit.flags.items(), key=lambda x: x[1]):
			description.append(flag_pattern.format(flag=flag, descr=get_text(key, val)))

		description.append("")
		description.append(_("regular expressions:"))
		description.append(_("With regular expressions you can search for any line matching a certain pattern."))
		description.append(_("The syntax of regular expressions in this program is specified by the python re module."))
		description.append(_("https://docs.python.org/3/library/re.html#regular-expression-syntax"))

		parser.description += "\n\n" + "\n".join(description)

	def execute(self, args):
		if args.cmd == self.CMD_NEXT:
			self.assert_no_reverse(args)
			self.app.search_next()
		elif args.cmd == self.CMD_PREV:
			self.assert_no_reverse(args)
			self.app.search_prev()
		elif args.cmd == self.CMD_EDIT:
			self.assert_no_reverse(args)
			self.app.search_open_edit(clear=False)
		else:
			reverse = args.reverse
			self.app.search_open_edit(reverse=reverse)
	
	def assert_no_reverse(self, args):
		if args.reverse:
			cmd = "--%s" % args.cmd
			raise ValueError(_("--reverse is incompatible with {cmd}").format(cmd=cmd))


class select(commands.Command):

	"""
	Select a specific line in the current view.
	This is an extension of urwid's internal cursor command.

	If no arguments are given a text box is opened at the
	bottom of the window where you can paste in a hash.
	When you press enter `select hash_id` is called
	where hash_id is the text that you have inserted.

	If you are not in the log view and hash_id is given
	a new details view is opened instead of moving the cursor.
	"""

	@classmethod
	def init_parser(cls, parser):
		parser.add_argument("hash_id", nargs='?', help='a revision to jump to. '
		'In the log view this must be a hash which is at least as long as the displayed hashes. '
		'In the details view any valid id is allowed (see `man gitrevisions`). '
		'If the value starts with a colon the current hash is prepended to it. '
		'This implies that you can display the contents of a certain file at this point in time '
		'with ":filename from the details view. '
		'That was useful before `open --after` was implemented.')
		group = parser.add_mutually_exclusive_group()
		group.add_argument("--first-line", action='store_true')
		group.add_argument("--last-line", action='store_true')
		group.add_argument("--next-tag", action='store_true')
		group.add_argument("--prev-tag", action='store_true')
		group.add_argument("--next-section", action='store_true')
		group.add_argument("--prev-section", action='store_true')
		group.add_argument("--next-paragraph", action='store_true')
		group.add_argument("--prev-paragraph", action='store_true')
		group.add_argument("--prev-selection", action='store_true')
		group.add_argument("--next-selection", action='store_true')

	def execute(self, args):
		num_args = sum(bool(val) for val in vars(args).values())
		if num_args > 1:
			raise ErrorInCommand(_("only one argument may be given"))

		elif args.first_line:
			self.app.select_first_line()
		elif args.last_line:
			self.app.select_last_line()

		elif args.next_tag:
			self.app.select_tag(prev=False)
		elif args.prev_tag:
			self.app.select_tag(prev=True)

		elif args.next_section:
			self.app.select_next_section()
		elif args.prev_section:
			self.app.select_prev_section()

		elif args.next_paragraph:
			self.app.select_next_paragraph()
		elif args.prev_paragraph:
			self.app.select_prev_paragraph()

		elif args.prev_selection:
			self.app.select_prev_selection()
		elif args.next_selection:
			self.app.select_next_selection()

		elif args.hash_id:
			self.app.select_commit(args.hash_id)
		else:
			self.app.select_commit_open_edit()

class set(commands.Command):

	"""
	Change settings.

	The syntax is based on vim and ranger.
	You can change several settings at once.
	Each setting has one of the following formats:

	    `key=value`  Assign a value
	    `key!`       Toggle a boolean value or
	                 cycle through a list of possible values
	    `key`        Set a boolean value to true
	    `key?`       Query a value

	The allowed values for key and values are listed below in "available settings".

	You can set a setting to the value of another setting by using percent signs, e.g.

	    set color.title.commit.refnames.head-branch-sep=%color.title%

	This copies the value when executing the set command,
	if the value of color.title is changed later on that change
	does not automatically affect color.title.commit.refnames.head-branch-sep.
	Both settings must have the same data type.

	Aside from the settings provided by this program
	you can also configure git directly, see `git config --help`.
	For example:
	$ git config --global diff.wordRegex '[[:alpha:]]+|[[:digit:]]+|.'
	These settings can be overridden by command line arguments
	which you can add or remove using `option`.
	"""

	run_before_init = True

	KEY_VAL_SEP = "="
	TOGGLE_SUFFIX = "!"
	QUERY_SUFFIX = "?"
	CYCLE_SPLIT = ","

	reo_other_setting = re.compile(r'%(?P<key>[^%]+)%$')

	@classmethod
	def init_parser(cls, parser):
		parser.add_argument('setting', nargs='+')
		parser.add_argument('-c', '--cycle', action='store_true', help=_("Several values can be given for the same setting separated by commas, calling the command repeatedly will cycle through the given values"))

	@classmethod
	def init_help_lines(cls, parser):
		super().init_help_lines(parser)
		out = cls.help_lines

		out.append("")
		out.append(_("data types:"))
		data_types = (
			(_("enum"), _("A set of allowed values")),
			(_("int"), _("E.g. 42 or 0x23")),
			(_("float"), _("E.g. 0.1")),
			(_("str"), _("One or several arbitrary characters")),
			(_("color"), _("foreground[,emphases][/background]")),
			("",         _("The square brackets indicate that emphasis and background are optional.")),
			("",         _("Several emphasis values can be given separated by commas.")),
			("",         _("foreground colors:")),
			("",         _("    default")),
			("",         _("    black, red, green, yellow, blue, magenta, cyan, white")),
			("",         _("    bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, bright white")),
			("",         _("emphases:")),
			("",         _("    bold, underline, standout, italics, blink, strikethrough")),
			("",         _("background colors:")),
			("",         _("    default, black, red, green, yellow, blue, magenta, cyan, white")),
			("",         _("Bright colors do not work with curses, see %app.display-module%.")),
			(_("coloredstr"), _("A str which may contain markup for colors:")),
			("",              _("<color=value>...</color>")),
			("",              _("where value is a color as explained for data type color")),
			(_("cmd"), _("A shell command to generate the content to be displayed")),
			("",       _("(This is not actually executed in a shell, shell command as opposed to the internal commands which can be mapped to keys.)")),
			("",       _("This is usually a git command but can be replaced by a custom script.")),
			("",       _("Additionally a few specialized internal functions are available (see below).")),
			("",       _("Several subprocesses can be given, separated by a semicolon. Their outputs are concatenated.")),
			("",       _("The syntax is shell-like, parsed with shlex.shlex(value, posix=True, punctuation_chars=';') and whitespace_split=True.")),
			(_("list"), _("A comma separated list of an arbitrary number of items")),
		)
		out.extend(cls.AlignedLine("  "+ln) for ln in utils.format_table(data_types, col_sep="  ^"))

		cls.add_internal_functions_to_help(out, "log view", model.LogModel)
		cls.add_internal_functions_to_help(out, "details view", model.DetailsModel)
		cls.add_available_settings_to_help(out)

	@classmethod
	def add_internal_functions_to_help(cls, out, view, model):
		out.append("")
		out.append(_("internal functions which can be used in log view:").format(view=view))
		for funcname in sorted(model.command_functions.keys()):
			func = model.command_functions[funcname]
			funcname = model.INTERNAL_FUNCTION_PREFIX + funcname
			funcargs = getattr(func, 'arguments', '')
			funcdesc = getattr(func, 'description', '')
			funcconf = getattr(func, 'settings', [])
			out.append("  " + funcname + " " + funcargs)
			if funcdesc:
				out.append("      " + funcdesc)
			if funcconf:
				out.append("      Related settings:")
				pattern =  "          %{}%"
				for key in funcconf:
					out.append(pattern.format(key))

	@classmethod
	def add_available_settings_to_help(cls, out):
		out.append("")
		out.append(_("available settings:"))

		key_width = len(max(settings.keys(), key=len))
		fmt = "  {key:%s}  {align_character}{allowed_values}" % key_width
		last_group = None
		for key in settings.keys():
			group = key.split(settings.GROUP_SEP, 1)[0]
			if last_group and group != last_group:
				out.append("")
			last_group = group

			attr, allowed_values, helpstr = settings.get(key)
			formatted_allowed_values = "%s: %s" % (settings.label_allowed_values(allowed_values), settings.format_allowed_values(allowed_values))
			ln = fmt.format(key=key, allowed_values=formatted_allowed_values, align_character=cls.app.align_character)
			if helpstr:
				ln += "\n" + helpstr
			if isinstance(allowed_values, (tuple, list)):
				if allowed_values[0] == list:
					allowed_values = allowed_values[1]
				for valname, value, valhelp in settings.iter_allowed_values(allowed_values):
					if valhelp:
						ln += "\n%s: %s" % (valname, valhelp)
			ln = cls.AlignedLine(ln)
			out.append(ln)

	def execute(self, args):
		for s in args.setting:
			self.parse_setting(s, args)

	NO_VALUE = True
	TOGGLE_VALUE = None
	QUERY_VALUE = False

	def parse_setting(self, setting, args):
		i = setting.find(self.KEY_VAL_SEP)
		if i < 0:
			if setting.endswith(self.TOGGLE_SUFFIX):
				key = setting[:-len(self.TOGGLE_SUFFIX)]
				value = self.TOGGLE_VALUE
			elif setting.endswith(self.QUERY_SUFFIX):
				key = setting[:-len(self.QUERY_SUFFIX)]
				value = self.QUERY_VALUE
			else:
				key = setting
				value = self.NO_VALUE
		else:
			key = setting[:i]
			value = setting[i+len(self.KEY_VAL_SEP):]

		if key not in settings.keys():
			raise ErrorInCommand(_("unknown setting %s" % key))
		attr, allowed_values, help_str = settings.get(key)

		cycle = args.cycle
		value, is_allowed_value = self.parse_value(key, attr, value, allowed_values, cycle)
		if not is_allowed_value:
			return

		try:
			settings.rsetattr(self, attr, value)
		except Exception as e:
			raise ErrorInCommand("%s while trying to set %s" % (e, key))
		else:
			self.app.show_info(_("{key}={value}").format(key=key, value=settings.format_value(value, allowed_values)))

	def parse_value(self, key, attr, value, allowed_values, cycle):
		if value == self.QUERY_VALUE:
			value = settings.rgetattr(self, attr)
			self.app.show_info(_("{key}={value}").format(key=key, value=settings.format_value(value, allowed_values)))
			return None, False

		if value == self.TOGGLE_VALUE:
			if isinstance(allowed_values, (tuple, list)):
				value = settings.rgetattr(self, attr)
				allowed_values = list(settings.iter_allowed_values(allowed_values))
				for i in range(len(allowed_values)-1):
					itervalue = allowed_values[i][1]
					if value == itervalue:
						value = allowed_values[i+1][1]
						break
				else:
					value = allowed_values[0][1]
				return value, True

			raise ErrorInCommand(_("cannot toggle value of {key} (allowed values: {allowed_values})").format(key=key, allowed_values=settings.format_allowed_values(allowed_values)))

		if value == self.NO_VALUE:
			if settings.can_be_true(allowed_values):
				return True, True

			raise ErrorInCommand(_("missing value for {key} (allowed values: {allowed_values})").format(key=key, allowed_values=settings.format_allowed_values(allowed_values)))

		if cycle:
			current_value = settings.rgetattr(self.app, attr)
			first_possible_value = None
			found_current_value = False
			for val in value.split(self.CYCLE_SPLIT):
				val = self.parse_single_value(key, attr, val, allowed_values)
				if found_current_value:
					return val, True
				if val == current_value:
					found_current_value = True
				if first_possible_value is None:
					first_possible_value = val
			return first_possible_value, True

		else:
			value = self.parse_single_value(key, attr, value, allowed_values)
			return value, True

	def parse_single_value(self, key, attr, value, allowed_values):
		m = self.reo_other_setting.match(value)
		if m:
			other_key = m.group('key')
			try:
				other_attr, other_allowed_values, other_helpstr = settings.get(other_key)
			except KeyError:
				raise ErrorInCommand(_("no such setting {other_key}").format(other_key=other_key))
			if allowed_values != other_allowed_values:
				raise ErrorInCommand(_("{other_key} has other data type than {key}").format(key=key, other_key=other_key))
			return settings.rgetattr(self.app, other_attr), True

		if allowed_values == str:
			return value

		if allowed_values == settings.TYPE_COLOR:
			return value

		if allowed_values == settings.TYPE_COLORED_STR:
			return value

		if allowed_values == int:
			try:
				value = int(value, 0)
			except ValueError:
				raise ErrorInCommand(_("failed to parse int {value!r} which you have tried to assign to {key}").format(key=key, value=value))
			return value

		if allowed_values == float:
			try:
				value = float(value)
			except ValueError:
				raise ErrorInCommand(_("failed to parse float {value!r} which you have tried to assign to {key}").format(key=key, value=value))
			return value

		if isinstance(allowed_values, (tuple, list)):
			if allowed_values[0] == list:
				assert len(allowed_values) == 2
				allowed_values = allowed_values[1]
				out = []
				for v in value.split(","):
					v = self.parse_single_value(key, attr, v, allowed_values)
					out.append(v)
				return out

			for thisvalname, thisvalue, thishelp in settings.iter_allowed_values(allowed_values):
				if thisvalname == value:
					return thisvalue
			else:
				raise ErrorInCommand(_("invalid value {value!r} for {key} (expected one of {allowed_values})").format(value=value, key=key, allowed_values=settings.format_allowed_values(allowed_values)))

		if allowed_values == settings.TYPE_COMMAND:
			s = shlex.shlex(value, posix=True, punctuation_chars=';')
			s.whitespace_split = True
			out = [[]]
			for word in s:
				if word == ';':
					out.append([])
				else:
					out[-1].append(word)
			if len(out) == 1:
				out = out[0]
			return out

		raise ErrorInCommand(_("I don't know how to deal with data type {allowed_values} of {key}").format(allowed_values=settings.format_allowed_values(allowed_values), key=key))

class set2(set):

	"""
	This is the same like `set` except that it is executed after initialization.
	This may be useful for debugging if you want to change %app.log-level% in a config file.
	But in most cases this is not the command you are looking for.

	For more information on the loading of config files before and after initialization see the help of `config.load`.
	"""

	name = "set.after-init"

	run_before_init = False
	run_after_init = True

	# without overriding this method it would reuse the help of set
	# ignoring this class' doc string and using the name of the parent class
	@classmethod
	def init_help_lines(cls, parser):
		commands.Command.init_help_lines.__func__(cls, parser)


class bind(commands.Command):

	"""
	Define a keyboard shortcut.
	If cmd is a ? show all mappings which would be overwritten by (re)mapping key.
	If key is a ? show all mappings where the command or fallback command starts with cmd.
	In order to map the key ? wrap it in angular brackets: <?>

	key is a sequence of one or more keys to be pressed in order to run cmd.
	Each of these keys is generally specified in the same way as urwid passes them to keypress.
	Exceptions are the three keys SPACE, LESS and GREATER (see the examples below).
	Key representations longer than one character are wrapped in angular brackets.
	Keys to be pressed at the same time are treated like one key, i.e. the keys are placed in the same pair of angular brackets.
	Keys to be pressed after one another are concatenated without a separator.

	Some key combinations are intercepted by the terminal to insert control characters.
	https://github.com/urwid/urwid/issues/140

	cmd is either a Primitive Command or a Programmable Command
	possibly followed by one or more arguments (see `help --commands`).
	Primitive commands can only be assigned to a single key or a combination of keys which
	are pressed at the same time. Primitive commands cannot be assigned to a combination of
	keys where the keys are pressed after each other.

	You need to quote cmd (and key) if it contains spaces.
	Splitting the arguments is done using shlex.split
	so quoting works similar to a shell.

	example key combinations (pressed at the same time):
	  -------------------------------------
	  | input          | key              |
	  -------------------------------------
	  | H              | h                |
	  | SHIFT+H        | H                |
	  | ENTER          | <enter>          |
	  | TAB            | <tab>            |
	  | UP             | <up>             |
	  | PAGE DOWN      | <page down>      |
	  | F5             | <f5>             |
	  | SHIFT+F5       | <shift f5>       |
	  | CTRL+SHIFT+F5  | <shift ctrl f5>  |
	  | ALT+J          | <meta j>         |
	  -------------------------------------
	  | SPACE          | <space>          |
	  | <              | <less>           |
	  | >              | <greater>        |
	  -------------------------------------

	  see also http://urwid.org/manual/userinput.html#keyboard-input

	example key combinations intercepted by the terminal:
	  ---------------------------------------------
	  | input          | key/effect               |
	  ---------------------------------------------
	  | CTRL+I         | <tab>                    |
	  | CTRL+SPACE     | <<0>>                    |
	  ---------------------------------------------
	  | CTRL+C         | close                    |
	  | CTRL+S         | stop updating screen     |
	  | CTRL+Q         | resume updating screen   |
	  ---------------------------------------------

	  https://github.com/urwid/urwid/issues/140
	"""

	name = "map"

	@classmethod
	def init_parser(cls, parser):
		parser.add_argument('key')
		parser.add_argument('cmd')
		parser.add_argument('-m', '--mnemonic')

	def execute(self, args):
		if args.key == '?' and args.cmd == '?':
			self.app.show_keyboard_shortcuts()
		elif args.key == '?':
			self.app.show_mapped_keys(args.cmd)
		elif args.cmd == '?':
			self.app.show_mapped_commands(args.key)
		else:
			cmd = args.cmd
			if args.mnemonic:
				cmd = utils.CommandWithMnemonic(cmd, args.mnemonic)
			self.app.bind_key(args.key, cmd)

class unmap(commands.Command):

	"""
	Remove a keyboard shortcut.

	If key is {KEY_ALL} remove all keyboard shortcuts.
	"""

	@classmethod
	def init_help(cls, parser):
		super().init_help(parser)
		if len(cls.app.KEY_ALL) == 1:
			parser.description += "\n" + _("In order to unmap the key {KEY_ALL} wrap it in angular brackets: <{KEY_ALL}>")
		parser.description += "\n\n" + _("The syntax of key is explained in the help of `map`.")
		parser.description = parser.description.format(KEY_ALL=cls.app.KEY_ALL)

	@classmethod
	def init_parser(cls, parser):
		parser.add_argument('key')

	def execute(self, args):
		self.app.unbind_key(args.key)

class bind_fallback(commands.Command):

	"""
	Define a fallback command.
	If fallback is a ? show the mapping which would be overwritten by (re)mapping primitive.
	If primitive is a ? show all primitive commands which have cmd as fallback command.

	Each primitive command can be assigned a programmable command as fallback.
	The fallback command is executed in case the primitive command is not consumed by any widget.
	"""

	name = "map-fallback"

	@classmethod
	def init_parser(cls, parser):
		parser.add_argument('primitive')
		parser.add_argument('fallback')

	def execute(self, args):
		if args.primitive == '?' and args.fallback == '?':
			table = list(self.app.iter_commandmap_items(self.app.command_fallback))
			if not table:
				self.app.show_info(_("there are no fallback commands"))
				return
			width = lambda col: len(max((row[col] for row in table), key=len))
			col_widths = [width(col) for col in range(2)]
			table = [tuple(row[col].ljust(col_widths[col]) for col in range(2)) for row in table]
			out = "\n".join("  %s || %s" % row for row in table)
			self.app.show_info(_("fallback commands:\n") + out)
		elif args.primitive == '?':
			primitives = [prim for prim, fallback in self.app.iter_commandmap_items(self.app.command_fallback) if fallback==args.fallback]
			if primitives:
				self.app.show_info(_("the following primitive commands have `{fallback}` as fallback command:{primitives}")
					.format(fallback=args.fallback, primitives="".join(_("\n  {cmd}").format(cmd=cmd) for cmd in primitives)))
			else:
				self.app.show_info(_("no primitive commands have `{fallback}` as fallback command").format(fallback=args.fallback))
		elif args.fallback == '?':
			fallback = self.app.command_fallback[args.primitive]
			if fallback:
				self.app.show_info(_("`{fallback}` is the fallback command of `{primitive}`").format(fallback=fallback, primitive=args.primitive))
			else:
				self.app.show_info(_("no fallback command for `{primitive}`").format(primitive=args.primitive))
		else:
			self.app.bind_fallback(args.primitive, args.fallback)

class unmap_fallback(commands.Command):

	"""
	Remove a fallback command.

	If key is {KEY_ALL} remove all fallback commands.
	"""

	@classmethod
	def init_help(cls, parser):
		super().init_help(parser)
		parser.description = parser.description.format(KEY_ALL=cls.app.KEY_ALL)

	@classmethod
	def init_parser(cls, parser):
		parser.add_argument('primitive', help=_("The primitive command from which you want to remove the fallback command"))

	def execute(self, args):
		self.app.unbind_fallback(args.primitive)

class link(commands.Command):

	"""
	Follow a link.
	Displays a hint in square brackets after everything which looks like a hash id.
	Press the keys indicated by the hint to open the corresponding git object.
	"""

	run_before_init = False
	run_after_init = False

	def execute(self, args):
		self.app.show_hints(self.app.follow_link)

class resize(commands.Command):

	"""
	If you are in horizontal or vertical layout
	change the size of the currently focused view.

	The layout can be switched using the command `layout`.
	"""

	@classmethod
	def init_parser(cls, parser):
		parser.add_argument('--move-border', '-m', action='store_true', help=_("Move the right border of the currently focused view or the left border if the currently focused view is the right most view (instead of increasing the size of the currently focused view and decreasing the size of all other views)"))
		parser.add_argument('step', type=int, help=_("How much to increase the size of the current view in percent of the complete window size. Pass a negative number to decrease the size."))

	def execute(self, args):
		if args.move_border:
			self.app.move_view_border(args.step)
		else:
			self.app.change_view_size(args.step)

class visual(commands.Command):

	"""
	Enter or leave visual mode.
	In visual mode single lines can be selected.
	This is entered automatically when using the search command.

	Turn visual mode on to select a line you want to open in an external editor.
	Turn visual mode off for more comfortable scrolling.
	"""

	@classmethod
	def init_parser(cls, parser):
		group = parser.add_mutually_exclusive_group()
		group.add_argument("--on",  action='store_const', dest='arg', const=cls.app.VISUAL_ON,  help=_("Lines can be selected"))
		group.add_argument("--off", action='store_const', dest='arg', const=cls.app.VISUAL_OFF, help=_("Lines cannot be selected"))
		group.add_argument("--toggle", action='store_const', dest='arg', const=cls.app.VISUAL_TOGGLE, help=_("Toggle between --on and --off"))
		group.set_defaults(arg=cls.app.VISUAL_ON)

	def execute(self, args):
		self.app.visual(args.arg)

class yank(commands.Command):

	"""
	Copy information.

	The information to be copied is determined by the format argument.
	If several format arguments are given they are concatenated with a separating space in between.
	All placeholders supported by `git for-each-ref --format` (if a tag is open) or `git log --format` (otherwise) can be used.
	Additionally the following human readable placeholders are supported:
	"""

	SELECTION_PRIMARY = "primary"
	SELECTION_CLIPBOARD = "clipboard"

	placeholders = {
		"hash" : "%H",
		"short hash" : "%h",
		"subject" : "%s",
		"body"  : "%b",
		"contents"  : "%B",
		# copy author name/email but committer date because
		# those are the values that are displayed in the log
		"name"  : "%an",
		"email" : "%ae",
		"date"  : "%ci",
		"author" : "%an <%ae>",
		"author name"  : "%an",
		"author email" : "%ae",
		"author date"  : "%ai",
		"committer" : "%cn <%ce>",
		"committer name"  : "%cn",
		"committer email" : "%ce",
		"committer date"  : "%ci",
	}
	placeholders_tag = {
		"subject" : "%(subject)",
		"body" : "%(body)",
		"contents" : "%(contents)",
		"name" : "%(taggername)",
		"email" : "%(taggeremail)",
		"date" : "%(taggerdate:iso)",
		"hash" : "%(objectname)",
		"short hash" : "%(objectname:short)",
	}
	placeholders_any = {
		"id" : "get_id",
		"cwd" : "get_cwd",
		"type" : "get_type",
		"last search term" : "get_last_search_term",
		"path" : "get_rel_path",
		"relative path" : "get_rel_path",
		"absolute path" : "get_abs_path",
	}

	@classmethod
	def init_parser(cls, parser):
		# Sort placeholders by length so that the longest possible match is replaced first.
		# Otherwise it might happen that the key "committer date" is interpreted
		# as the key "committer" followed by the suffix " date".
		cls.sorted_placeholders = [(key,val) for key,val in cls.placeholders.items()]
		cls.sorted_placeholders.sort(key=lambda o: len(o[0]), reverse=True)
		cls.sorted_placeholders_tag = [(key,val) for key,val in cls.placeholders_tag.items()]
		cls.sorted_placeholders_tag.sort(key=lambda o: len(o[0]), reverse=True)
		cls.sorted_placeholders_any = [(key,val) for key,val in cls.placeholders_any.items()]
		cls.sorted_placeholders_any.sort(key=lambda o: len(o[0]), reverse=True)

		parser.add_argument("format", nargs='*', default='hash')
		parser.add_argument("--primary",   "-p", dest="selection", action="store_const", const=cls.SELECTION_PRIMARY, default=cls.SELECTION_CLIPBOARD)
		parser.add_argument("--clipboard", "-c", dest="selection", action="store_const", const=cls.SELECTION_CLIPBOARD)
		parser.add_argument("--no-git", "-n", action="store_true", help=_("Do not replace git placeholders (works also with unstaged and uncommitted changes)"))
		parser.add_argument("--follow", "-f", action="store_true", help=_("Select a hash id which you want to copy the information for (like with the command `link`)"))
		parser.add_argument("--verbose", action="store_true", help=_("Show the command used to copy the information"))

	@classmethod
	def init_help(cls, parser):
		super().init_help(parser)
		placeholders = []
		for title, placeholders_map, _help in (
			(_("placeholders for commits"), cls.placeholders, lambda val: val),
			(_("placeholders for tags"), cls.placeholders_tag, lambda val: val),
			(_("placeholders for all types"), cls.placeholders_any, lambda val: getattr(cls, val).__doc__),
		):
			placeholders.append("\n%s:" % title)
			for wc in sorted(placeholders_map.keys()):
				placeholders.append(_("- %s (%s)") % (wc, _help(placeholders_map[wc])))

		placeholders = "\n".join(placeholders)
		parser.description += "\n" + placeholders


	def execute(self, args):
		self.verbose = args.verbose
		if args.follow:
			self.app.show_hints(lambda hint_type, hash_id: self.execute2(args, hint_type, hash_id, self.app.TYPE_OTHER))
		else:
			hash_id, type_id = self.app.get_current_hash_id()
			self.execute2(args, self.app.HINT_TYPE_HASH, hash_id, type_id)

	def execute2(self, args, hint_type, hash_id, type_id):
		selection = args.selection

		fmt = args.format
		fmt = " ".join(fmt)

		if hint_type != self.app.HINT_TYPE_HASH:
			return fmt.replace("id", hash_id)

		if args.no_git:
			out = fmt
			for human_readable, func in self.sorted_placeholders_any:
				out = re.sub(r'\b%s\b' % human_readable, lambda m: getattr(self, func)(hash_id, type_id), out)
			self.copy(out, selection)
			return

		if hash_id is None:
			raise ErrorInCommand(_("no commit selected"))
		if hash_id in (self.app.ID_STAGED, self.app.ID_UNSTAGED, self.app.ID_UNTRACKED):
			raise ErrorInCommand(_("uncommitted changes have no meta info which could be copied"))
		if hash_id in (self.app.ID_STASHES_GROUP,):
			raise ErrorInCommand(_("please open the group and select the stash you want to copy"))

		if type_id == self.app.TYPE_TAG:
			sorted_placeholders = self.sorted_placeholders_tag
		else:
			sorted_placeholders = self.sorted_placeholders

		for human_readable, git_readable in sorted_placeholders:
			fmt = re.sub(r'\b%s\b' % human_readable, git_readable, fmt)
		for human_readable, func in self.sorted_placeholders_any:
			fmt = re.sub(r'\b%s\b' % human_readable, lambda m: getattr(self, func)(hash_id, type_id), fmt)

		if type_id == self.app.TYPE_TAG:
			cmd = ["git", "for-each-ref", "--format", fmt, "refs/tags/%s" % hash_id]
		else:
			cmd = ["git", "log", "-1", "--pretty=format:%s" % fmt, hash_id, "--"]
		out = self.run_and_get_output(cmd)
		out = out.rstrip("\n")

		self.copy(out, selection)

	# ------- commands -------

	def get_id(self, hash_id, type_id):
		"""The internally used id; except for commits, where it copies the full hash instead of the short hash"""
		if type_id == self.app.TYPE_OTHER:
			return "%H"
		return hash_id

	def get_cwd(self, hash_id, type_id):
		"""Current working directory"""
		return os.getcwd()

	def get_type(self, hash_id, type_id):
		"""Git object type"""
		if hash_id in (self.app.ID_STAGED, self.app.ID_UNSTAGED, self.app.ID_UNTRACKED, self.app.ID_STASHES_GROUP):
			return hash_id
		return model.get_object_type(hash_id)

	def get_last_search_term(self, hash_id, type_id):
		"""The last search term"""
		search_edit = self.app.search_edit
		if not search_edit:
			raise ErrorInCommand(_("nothing has been searched for yet"))
		return self.app.search_edit.get_last_input()

	def get_rel_path(self, hash_id, type_id):
		"""In details view: The path of the current file relative to the current working directory"""
		return self.app.get_current_file_path()

	def get_abs_path(self, hash_id, type_id):
		"""In details view: The absolute path of the current file"""
		fn = self.app.get_current_file_path()
		if fn:
			fn = os.path.abspath(fn)
		return fn


	# ------- copy -------

	def copy(self, text, selection):
		if self.has_wlcopy():
			self.copy_wlcopy(text, selection)
		elif self.has_xsel():
			self.copy_xsel(text, selection)
		elif self.has_xclip():
			self.copy_xclip(text, selection)
		else:
			raise ErrorInCommand(_("please install wl-copy, xsel or xclip in order to use this feature"))

		self.app.show_success(_("copied %r") % text)


	def copy_wlcopy(self, text, selection):
		cmd = ["wl-copy"]
		if selection == self.SELECTION_PRIMARY:
			cmd.append("--primary")
		cmd.append("--")
		cmd.append(text)

		if self.verbose:
			self.app.show_info(shlex.join(cmd))
		self.run(cmd, check=True)

	def copy_xsel(self, text, selection):
		if selection == self.SELECTION_PRIMARY:
			selection = "--primary"
		else:
			selection = "--clipboard"

		cmd = ["xsel", "-i", selection]
		if self.verbose:
			self.app.show_info(shlex.join(cmd))
		self.run(cmd, stdin=text, check=True)

	def copy_xclip(self, text, selection):
		if selection == self.SELECTION_PRIMARY:
			selection = "primary"
		else:
			selection = "clipboard"

		cmd = ["xclip", "-in", "-selection", selection]
		if self.verbose:
			self.app.show_info(shlex.join(cmd))
		self.run(cmd, stdin=text, check=True)


	def has_wlcopy(self):
		cmd = ["wl-copy", "--version"]
		return self.run(cmd, check=False) == 0

	def has_xsel(self):
		cmd = ["xsel", "--version"]
		return self.run(cmd, check=False) == 0

	def has_xclip(self):
		cmd = ["xclip", "-version"]
		return self.run(cmd, check=False) == 0

class add_editor(commands.Command):

	"""
	Create settings for another editor.

	When git-viewer opens a file in an external editor it needs to know
	how to specify the line number to jump to and how to open a file read only.
	The editor to be used is specified by the environment variable EDITOR.
	vi, vim and nano are supported out of the box but if you want to use
	a different editor you can create the required settings for it with this command.

	The settings for the new editor are added in the name space editor.<name>.

	example:
	  add-editor vim --linenumber=+{ln} --readonly=-R
	"""

	name = "add-editor"

	@classmethod
	def init_parser(cls, parser):
		parser.add_argument("name", help=_("The name which is used in the settings for this editor. This is usually the same like the command to be executed, i.e. the value of EDITOR, but if it's not you can set that later by changing the setting editor.<name>.command."))
		parser.add_argument("-l", "--linenumber", default="", help=_("A command line argument to be added to the editor command to specify the line number, should include the wildcard {ln}"))
		parser.add_argument("-r", "--readonly", default="", help=_("A command line argument to be added to the editor command to specify that the file is supposed to be opened read only"))

	def execute(self, args):
		self.app.model.opener.add_editor(args.name, linenumber=args.linenumber, readonly=args.readonly)

class debug(commands.Command):

	"""
	Debug functions
	"""

	@classmethod
	def init_parser(cls, parser):
		group = parser.add_mutually_exclusive_group()
		group.add_argument("--show-line-id", action='store_true')
		group.add_argument("--show-screen-type", action='store_true', help=_("If %%app.display-module%% is auto you can use this to check which display module was loaded"))
		group.add_argument("--show-main-views-index", action='store_true')

	def execute(self, args):
		if args.show_line_id:
			self.app.debug_show_line_id()
		elif args.show_screen_type:
			self.app.show_info("screen type: %s" % type(self.app.screen))
		elif args.show_main_views_index:
			self.app.show_info("main_views_index: %s" % self.app.main_views_index)
		else:
			raise ErrorInCommand("debug functionality not implemented")


if __name__ == '__main__':
	import api_commands
	import main
	cmdcont = api_commands.CommandContainer(main.App())
	cmdcont.load_commands_from_list(locals().values())
