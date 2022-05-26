#!/usr/bin/env python3

import shlex
import gettext
_ = gettext.gettext

from .urwid_text_layout import LogTextLayout as TextLayout

ATTR_SEP = '.'
GROUP_SEP = '.'

WC_HASH_ID = "{hash}"

BOOL_TRUE = "true"
BOOL_FALSE = "false"
VAL_AUTO = "auto"
VAL_APP = "app"

TYPE_COMMAND = "cmd"
TYPE_COLOR = "color"
TYPE_COLORED_STR = "coloredstr"

PATTERNS = {
	TYPE_COLOR : _("foreground[,emphases][/background]"),
}

VIEW_MODE_VER = "ver"
VIEW_MODE_HOR = "hor"
VIEW_MODE_ONE = "one"

BACKEND_CURSES = "curses"
BACKEND_RAW = "raw"

LOG_FOCUS_FIRST_LINE = "first-line"
LOG_FOCUS_UNTRACKED = "untracked-files"
LOG_FOCUS_UNSTAGED = "unstaged-changes"
LOG_FOCUS_STAGED = "staged-changes"
LOG_FOCUS_LATEST_COMMIT = "latest-commit"

COLOR_TITLE  = "color.title"
COLOR_SUBTITLE  = "color.subtitle"
COLOR_DECORATION_BRANCH_LOCAL = "color.title.commit.refnames.branch.local"
COLOR_DECORATION_BRANCH_REMOTE = "color.title.commit.refnames.branch.remote"
COLOR_DECORATION_TAG = "color.title.commit.refnames.tag"
COLOR_DECORATION_HEAD = "color.title.commit.refnames.head"
COLOR_DECORATION_HEAD_BRANCH_SEP = "color.title.commit.refnames.head-branch-sep"
COLOR_INFO = "color.echo.info"
COLOR_WARNING = "color.echo.warning"
COLOR_ERROR = "color.echo.error"
COLOR_SUCCESS = "color.echo.success"
COLOR_HINT = "color.link.hint"
COLOR_LINK = "color.link.hash"
COLOR_ELLIPSIS = "color.ellipsis"
COLOR_SPECIAL_CHARACTER = "color.special-character"
COLOR_KEY = "color.shortcut.key"
COLOR_KEY_PRESSED = "color.shortcut.key.pressed"
COLOR_MNEMONIC = "color.shortcut.mnemonic"
COLOR_CMD = "color.shortcut.cmd"
COLOR_KEY_IN_TEXT = "color.help.key"
COLOR_CMD_IN_TEXT = "color.help.cmd"
COLOR_CMD_IN_LINK = "color.link.cmd"
COLOR_LOG_STAGED = "color.log-entry.staged"
COLOR_LOG_UNSTAGED = "color.log-entry.unstaged"
COLOR_LOG_UNTRACKED = "color.log-entry.untracked"
COLOR_LOG_STASHES = "color.log-entry.stashes"
COLOR_DETAILS_UNTRACKED = "color.details-view.line-pattern-untracked"
COLOR_LINE_NUMBERS = "color.linenumber"
COLORS = (
	COLOR_TITLE, COLOR_SUBTITLE,
	COLOR_DECORATION_BRANCH_LOCAL, COLOR_DECORATION_BRANCH_REMOTE, COLOR_DECORATION_TAG, COLOR_DECORATION_HEAD,
	COLOR_DECORATION_HEAD_BRANCH_SEP,
	COLOR_INFO, COLOR_WARNING, COLOR_ERROR, COLOR_SUCCESS,
	COLOR_HINT, COLOR_LINK,
	COLOR_ELLIPSIS, COLOR_SPECIAL_CHARACTER,
	COLOR_KEY_PRESSED, COLOR_KEY, COLOR_CMD, COLOR_MNEMONIC,
	COLOR_CMD_IN_TEXT, COLOR_KEY_IN_TEXT, COLOR_CMD_IN_LINK,
	COLOR_LOG_STAGED, COLOR_LOG_UNSTAGED, COLOR_LOG_UNTRACKED, COLOR_LOG_STASHES,
	COLOR_DETAILS_UNTRACKED,
	COLOR_LINE_NUMBERS,
)

LOG_LEVEL_ALL = 0
LOG_LEVEL_INFO = 10
LOG_LEVEL_SUCCESS = 15
LOG_LEVEL_WARNING = 20
LOG_LEVEL_ERROR = 30
LOG_LEVEL_NONE = 40

LOG_LEVEL_NAME_ALL = "all"
LOG_LEVEL_NAME_INFO = "info"
LOG_LEVEL_NAME_SUCCESS = "success"
LOG_LEVEL_NAME_WARNING = "warning"
LOG_LEVEL_NAME_ERROR = "error"
LOG_LEVEL_NAME_NONE = "none"

LOG_LEVELS = (
	(LOG_LEVEL_NAME_ALL, LOG_LEVEL_ALL),
	(LOG_LEVEL_NAME_INFO, LOG_LEVEL_INFO),
	(LOG_LEVEL_NAME_SUCCESS, LOG_LEVEL_SUCCESS),
	(LOG_LEVEL_NAME_WARNING, LOG_LEVEL_WARNING),
	(LOG_LEVEL_NAME_ERROR, LOG_LEVEL_ERROR),
	(LOG_LEVEL_NAME_NONE, LOG_LEVEL_NONE),
)

RELATIVE_ROOT = 'root'
RELATIVE_GIT = 'git'
RELATIVE_CWD = 'cwd'

relative_values = (
	(RELATIVE_CWD, RELATIVE_CWD, _("Paths relative to current working directory")),
	(RELATIVE_GIT, RELATIVE_GIT, _("Paths relative to git top level directory")),
	(RELATIVE_ROOT, RELATIVE_ROOT, _("Absolute paths")),
)

bool_values = ((BOOL_TRUE, True), (BOOL_FALSE, False))
align_values = (
	("left-indentation", TextLayout.ALIGN_INDENTATION, _("Left align but add an indentation to broken lines for better readability. The amount of indentation is specified by the align character %app.align-character%. The align character is not displayed and is automatically removed or restored from the commands when changing this option. If this character occurs several times in a line only the first occurence is treated as align character and the others are displayed normally. If a line contains no align character it is assumed to be present before the first character. I have implemented this align mode myself. If it causes trouble try urwid's default left.")),
	("left", TextLayout.ALIGN_LEFT),
	("center", TextLayout.ALIGN_CENTER),
	("right", TextLayout.ALIGN_RIGHT),
)
wrap_values = (
	("any", TextLayout.WRAP_ANY, _("Wrap lines, a line break is possible at any character")),
	("space", TextLayout.WRAP_SPACE, _("Wrap lines, a line break is possible at spaces")),
	("clip", TextLayout.WRAP_CLIP, _("Don't wrap lines")),
	("ellipsis", TextLayout.WRAP_ELLIPSIS, _("Don't wrap lines, insert an ellipsis if a line cannot be displayed completely (requires urwid 2.1.0 or later)")),
	#TextLayout.WRAP_CUSTOM,
)

settings = {
	# key : (attribute, type/allowed values, help)
	# allowed values: a list of (valname, value, helpstr) tuples. helpstr can be omitted. A single str can be used instead of the tuple if value is a str equal to valname and there is no help.
	"layout.preferred" : ("app.preferred_view_mode", (VIEW_MODE_HOR, VIEW_MODE_VER, VIEW_MODE_ONE), "Specify which layout should be used (if the window is big enough)."),
	"layout.required-width-for-hor" : ("app.min_width_for_hor", int, "Do not switch to horizontal layout automatically if the window is smaller than the specified amount of columns. This does not apply when switching the layout manually."),
	"layout.required-height-for-ver" : ("app.min_height_for_ver", int, "Do not switch to vertical layout automatically if the window is smaller than the specified amount of rows. This does not apply when switching the layout manually."),
	"layout.auto-switch-on-resize" : ("app.auto_switch_view_mode_on_resize", bool, "Automatically switch to a more appropriate layout if the window size changes."),

	"log-view.show-untracked" : ("app.LogModel.show_untracked", bool, _("Show untracked files (if existing) in the log.")),
	"log-view.show-untracked-as-separate-group" : ("app.LogModel.untracked_files_as_separate_group", (
		(BOOL_TRUE,  True,  _("Show untracked files separate from unstaged changes.")),
		(BOOL_FALSE, False, _("Show untracked files together with unstaged changes.")),
	), _("This setting is ignored if %log-view.show-untracked% is disabled.")),
	"log-view.show-stashes" : ("app.LogModel.show_stashed_changes", bool, _("Show stashed changes (if existing) in the log.")),
	"log-view.show-stashes-as-group" : ("app.LogModel.stashed_changes_group", (
		(BOOL_TRUE,  True,  _("Group all stashes to one list item. Opening that list item opens a list of all stashes.")),
		(BOOL_FALSE, False, _("Show one list item for each stash.")),
		(VAL_AUTO,   None,  _("{true} if there is more than one stash, {false} otherwise").format(true=BOOL_TRUE, false=BOOL_FALSE)),
	), _("This setting is ignored if %log-view.show-stashes% is disabled.")),
	"log-view.show-stashes-in-reverse-order" : ("app.LogModel.stashed_changes_reversed_order", (
		(BOOL_TRUE,  True,  _("Show oldest stash on top.")),
		(BOOL_FALSE, False, _("Show newest stash on top.")),
	), _("This setting is ignored if %log-view.show-stashes% is disabled. You may want to change this setting if you change %log-view.show-stashes-as-group%.")),
	"log-view.default-focus" : ("app.LogView.default_focus_lines", (list, (LOG_FOCUS_UNTRACKED, LOG_FOCUS_UNSTAGED, LOG_FOCUS_STAGED, LOG_FOCUS_LATEST_COMMIT, LOG_FOCUS_FIRST_LINE)), _("This setting determines which line to select when the program starts. If the first element of this list is not contained in the log view try the next.")),
	"log-view.fmt.log" : ("app.LogModel.fmt_log", str, "The value which is used for --custom-format if the command does not contain -g/--walk-reflogs (in %log-view.cmd.log% and %details-view.cmd.commit.referenced-by%). Regarding the allowed wild cards see `git log --help` section PRETTY FORMATS."),
	"log-view.fmt.reflog" : ("app.LogModel.fmt_reflog", str, "The value which is used for --custom-format if the command contains -g/--walk-reflogs (in %log-view.cmd.log%). Regarding the allowed wild cards see `git log --help` section PRETTY FORMATS."),
	"log-view.cmd.log" : ("app.LogModel.cmd_log", TYPE_COMMAND, "The command to generate the main part of the log view which shows the commits, --custom-format is replaced by %log-view.fmt.log% or %log-view.fmt.reflog%"),
	"log-view.cmd.stash-list" : ("app.LogModel.cmd_stash_list", TYPE_COMMAND, "The command to generate the list of stashes"),
	"log-view.cmd.unreachable" : ("app.LogModel.cmd_unreachable", TYPE_COMMAND, "The command to gather the unreachable commands if the command line argument --unreachable is used"),
	"log-view.line-pattern" : ("app.LogModel.ln_pattern", TYPE_COLORED_STR, _("How to format special log view entries such as staged and unstaged changes. If you change %log-view.cmd.log% you may want to adapt this. The value of this setting should include the wildcard {logentry}. Additionally to the color markup which can be used this is colored with one of %color.log-entry.*%.")),
	"log-view.line-pattern-error" : ("app.LogModel.ln_pattern_error", TYPE_COLORED_STR, _("This is displayed if one of the git commands %log-view.cmd.*% fails, the wild cards {err} and {cmd} are supported")),

	"details-view.auto-open" : ("app.is_auto_open_enabled", bool, "Automatically open the details when selecting a line. It may be useful to disable this if you are on a slow computer or are dealing with big commits."),
	"details-view.indent-broken-code" : ("app.DetailsModel.indent_broken_code", bool, "Move the align character to the next non-whitespace character (this requires align=left-indentation and can be influenced by %app.tab%)"),
	"details-view.max-lines-per-file" : ("app.DetailsView.max_lines_per_file", int, "Trim long diffs to reduce loading time."),
	"details-view.max-lines-per-file.blob" : ("app.DetailsView.max_lines_per_file_blob", int, "Trim long blobs to reduce loading time."),
	"details-view.show-untracked-relative-to" : ("app.DetailsModel.untracked_relative", relative_values, _("How to show untracked files")),
	"details-view.cmd.commit" : ("app.DetailsModel.cmd_pattern", TYPE_COMMAND, _("The command which generates the details view for a commit, should include the wild card {wc_hash}").format(wc_hash=WC_HASH_ID)),
	"details-view.cmd.tag" : ("app.DetailsModel.cmd_pattern_tag", TYPE_COMMAND, _("The command which generates the details view for a tag, should include the wild card {wc_hash}").format(wc_hash=WC_HASH_ID)),
	"details-view.cmd.blob" : ("app.DetailsModel.cmd_pattern_blob", TYPE_COMMAND, _("The command which generates the details view for a blob, should include the wild card {wc_hash}").format(wc_hash=WC_HASH_ID)),
	"details-view.cmd.tree" : ("app.DetailsModel.cmd_pattern_tree", TYPE_COMMAND, _("The command which generates the details view for a tree, should include the wild card {wc_hash}").format(wc_hash=WC_HASH_ID)),
	"details-view.cmd.stash" : ("app.DetailsModel.cmd_pattern_stashed", TYPE_COMMAND, _("The command which generates the details view for a stash, should include the wild card {wc_hash}").format(wc_hash=WC_HASH_ID)),
	"details-view.cmd.staged" : ("app.DetailsModel.cmd_staged", TYPE_COMMAND, _("The command which generates the details view for staged changes")),
	"details-view.cmd.unstaged" : ("app.DetailsModel.cmd_unstaged", TYPE_COMMAND, _("The command which generates the details view for unstaged changes")),
	"details-view.cmd.untracked" : ("app.DetailsModel.cmd_untracked", TYPE_COMMAND, _("The command which generates the details view for untracked changes, each line is formatted with %details-view.unstaged.line-pattern-untracked% or %details-view.untracked.line-pattern-untracked% and colored with %color.details-view.line-pattern-untracked%")),
	"details-view.cmd.diff" : ("app.DiffModel.cmd", TYPE_COMMAND, _("The beginning of the command which generates the content for gitd")),
	"details-view.cmd.commit.header-data" : ("app.DetailsModel.cmd_start_header_data", TYPE_COMMAND, _("The beginning of the command which gathers the data for the function $commitheader, format and commit hash are appended automatically")),
	"details-view.cmd.commit.referenced-by" : ("app.DetailsModel.cmd_referencing_commits", TYPE_COMMAND, _("The beginning of the command which generates the list of commits referencing the current commit in the function $referencedby, --grep is added automatically, --custom-format is replaced by %log-view.fmt.log%, the output is formatted by %details-view.commit.line-pattern-referenced-by%")),
	"details-view.untracked.line-pattern-untracked" : ("app.DetailsModel.ln_pattern_untracked_in_separate_group", TYPE_COLORED_STR, _("How to format untracked files displayed in a separate group (if %log-view.show-untracked-as-separate-group% is enabled or there are no other unstaged changes), should include the wildcard {filename}, additionally to the color markup which can be used this is colored with %color.details-view.line-pattern-untracked%")),
	"details-view.unstaged.line-pattern-untracked" : ("app.DetailsModel.ln_pattern_untracked_in_unstaged_changes", TYPE_COLORED_STR, _("How to format untracked files displayed together with unstaged changes (if %log-view.show-untracked-as-separate-group% is disabled), should include the wildcard {filename}, additionally to the color markup which can be used this is colored with %color.details-view.line-pattern-untracked%")),
	"details-view.commit.line-pattern-referenced-by" : ("app.DetailsModel.ln_pattern_referencedby", str, _("How to format an entry in the list of commits which reference the current commit, should include the wildcard {logentry}, this is related to %log-view.line-pattern% but does not support color markup, this should not contain an %app.align-character% if %details-view.cmd.commit.referenced-by% contains one")),
	"details-view.commit.user-pattern" : ("app.DetailsModel.pattern_user", TYPE_COLORED_STR, _("How to display a user in $commitheader, supported are the wild cards {name} and {email}")),
	"details-view.commit.indentation-commit-message" : ("app.DetailsModel.indent_body", str, _("An indentation for the commit message in $commitheader")),
	"details-view.line-numbers.min-width" : ("app.DetailsModel.min_line_number_width", int, _("The amount of space to reserve for line numbers is determined for each hunk individually and depends on the biggest line number, this setting can be used to always reserve space for at least a certain number of digits so that the line numbers column has the same width for all hunks")),
	"details-view.line-numbers.sep" : ("app.DetailsModel.linenumber_suffix", TYPE_COLORED_STR, _("A separator between the line number and the line itself")),
	"details-view.line-numbers.sep-left-right" : ("app.DetailsModel.linenumber_sep", TYPE_COLORED_STR, _("A separator between the left and right line number (when showing the line numbers before a merge commit)")),

	#TODO: after changing these settings n and ? are not updated automatically, a new search must be started
	"search.case-sensitive" : ("app.search_case_sensitive", bool_values + ((VAL_AUTO, None, _("Case sensitive if search text contains upper case characters, case insensitive otherwise")),), ""),
	"search.regex" : ("app.search_is_regex", bool, ""),

	"config.auto-reload" : ("app.is_auto_reload_config_enabled", bool, _("Automatically load the config file after `config.edit`")),

	"app.display-module" : ("app.backend", (VAL_AUTO, BACKEND_RAW, BACKEND_CURSES), "http://urwid.org/manual/displaymodules.html#raw-and-curses-display-modules"),
	# does not work. switches focus without updating main_views_index or updating the details view. and it does not even handle scrolling. I don't like this anyway, so I'm not gonna spend time on this.
	#"urwid.handle-mouse" : ("app.handle_mouse", bool_values, _("{true} means that urwid handles mouse events. I hate this option because it means that you cannot select text with the mouse and copy it.").format(true=BOOL_TRUE, false=BOOL_FALSE)),
	"app.tab" : ("app.DetailsView.TAB", str, "urwid can't leave handling of tabs to the terminal, it needs to know exactly how wide a character is, otherwise it couldn't handle linebreaks correctly. This setting says what to display instead of a tab character."),
	"app.align" : ("app.align", align_values, _("How to align lines, see also %details-view.align%")),
	"details-view.align" : ("app.DetailsView.align", ((VAL_APP, VAL_APP, _("Use same value like %app.align%")),)+align_values, _("How to align lines in details view")),
	"app.align-character" : ("app.align_character", str, _("If %app.align% is left-indentation this character specifies how far a broken line is supposed to be indented.")),
	"app.wrap" : ("app.wrap", wrap_values, _("Whether or how to wrap lines, see also %details-view.wrap%")),
	"details-view.wrap" : ("app.DetailsView.wrap", ((VAL_APP, VAL_APP, _("Use same value like %app.wrap%")),)+wrap_values, _("Whether or how to wrap lines in details view")),
	"app.show-focus-in-all-views" : ("app.show_focus_in_all_views", (
		(BOOL_TRUE, True, _("The selected line is highlighted in all displayed views")),
		(BOOL_FALSE, False, _("The selected line is highlighted in the focused view only")),
	), _("Only relevant if layout is {hor} or {ver}").format(hor=VIEW_MODE_HOR, ver=VIEW_MODE_VER)),
	"app.explicit-spaces" : ("app.explicit_spaces", bool, _("A workaround to avoid duplicates of full width characters appearing in the first column of indentation in some terminals with align=left-indentation. Requires urwid 2.1.0 or later. A side effect can be different highlighting of indentation in the selected row.")),
	"app.log-level" : ("app.log_level", LOG_LEVELS, _("Show messages only if they have this or a higher importance (this refers to the status bar only, at the moment this program does not write any log files)")),
	"app.command-pipe-poll-time" : ("app.POLL_TIME_S", float, "Number of seconds. Time period in which it is checked whether something has been read from the command pipe."),

	"app.pattern.error-in-command" : ("app.pattern_error_in_command", TYPE_COLORED_STR, _("How to format an error message from a command, {err} is the error message and {cmd} is the command which was executed, this pattern is expected to contain an %app.align-character%, this is colored with %color.echo.error%")),
	"app.pattern.mnemonic" : ("app.pattern_mnemonic", TYPE_COLORED_STR, _("Appended after a keyboard shortcut if it has a mnemonic, should include the wildcard {mnemonic}, this is colored with %color.shortcut.mnemonic%")),

	"link.hint-pattern" : ("app.Hintable.hint_pattern", TYPE_COLORED_STR, _("How to format the hint indicating which keys you need to press in order to follow a link, see `link`, this is colored using %color.link.hint%")),
	"link.hint-alphabet" : ("app.Hintable.HINTS_ALPHABET", str, _("The set of characters from which link hints are generated, earlier characters are preferred, must contain two characters minimum")),

	# I am not putting the titles in log-view or details-view because they are used in both
	"title.untracked" : ("app.model.title_untracked", str, _("Log entry and details view title for untracked files (if %log-view.show-untracked% is true)")),
	"title.unstaged" : ("app.model.title_unstaged", str, _("Log entry and details view title for unstaged changes")),
	"title.untracked-and-unstaged" : ("app.model.title_unstaged_and_untracked", str, _("Log entry and details view title for a combination of untracked files and unstaged changes (if %log-view.show-untracked-as-separate-group% is false and %log-view.show-untracked% is true)")),
	"title.staged" : ("app.model.title_staged", str, _("Log entry and details view title for staged changes")),
	"title.stashes" : ("app.model.title_stashes_group", str, _("Log entry and details view title for the list of all stashes (if %log-view.show-stashes% and %log-view.show-stashes-as-group% are not false)")),
	# this is used in details-view only but seperating it from the other titles would not make sense
	"title.commit" : ("app.model.title_commit", str, _("Title displayed in the details view for commits, the following wild cards are supported: {hash_id}, {refnames} (see %title.commit.refnames%), {subject}, {committer_name}, {committer_email}, {committer_date}, {author_name}, {author_email}, {author_date}, {body}")),
	"title.commit.refnames" : ("app.model.pattern_refnames", str, _("A pattern how to format {refnames} in %title.commit% if the commit has ref names (decorations), this pattern should include the wild card {refnames}")),
	"title.commit.refnames.sep" : ("app.model.refnames_sep", str, _("The seperator used in %title.commit.refnames% between different branches and tags")),
	"title.commit.refnames.head-branch-sep" : ("app.model.DetailsModel.decoration_head_branch_sep", str, _("The seperator used in %title.commit.refnames% between HEAD and the branch which HEAD is pointing to")),

	"help.pattern.cmd-with-key" : ("app.pattern_cmd_with_key", TYPE_COLORED_STR, _("How to format a command in the help if one or more keyboard shortcuts are mapped to the command, should contain the wildcards {cmd} or {keys}, cmd is colored with %color.help.cmd%, keys are colored with %color.help.key%")),
	"help.pattern.cmd-without-key" : ("app.pattern_cmd_without_key", TYPE_COLORED_STR, _("How to format a command in the help if no keyboard shortcut is mapped to the command, should contain the wildcard {cmd}, cmd is colored with %color.help.cmd%")),
	"help.key-sep" : ("app.sep_shortcut", str, _("The separator inserted between two keyboard shortcuts if several keyboard shortcuts are assigned to the same command")),
	"help.show-all-shortcuts" : ("app.help_show_all_shortcuts", (
		(BOOL_TRUE, True, _("Show all keyboard shortcuts for the command regardless of the given arguments")),
		(BOOL_FALSE, False, _("Show only those keyboard shortcuts which start with the same arguments")),
	), _("In the help of a command with arguments (when opened with `link` or `help --shortcuts`)")),
}

for color in COLORS:
	settings[color] = ("app.%s" % color.replace('.', '_'), TYPE_COLOR, "")



def keys():
	return sorted(settings.keys())

def get(key):
	attr, allowed_values, helpstr = settings[key]

	if allowed_values == bool:
		allowed_values = bool_values

	return attr, allowed_values, helpstr

def iter_allowed_values(allowed_values):
	for val in allowed_values:
		if isinstance(val, tuple):
			if len(val) == 3:
				valname, value, helpstr = val
			else:
				valname, value = val
				helpstr = None
		else:
			valname = val
			value = val
			helpstr = None
		yield valname, value, helpstr

def format_allowed_values(allowed_values):
	if isinstance(allowed_values, (tuple, list)):
		if allowed_values[0] == list:
			assert len(allowed_values) == 2
			return format_allowed_values(allowed_values[1])
		return ", ".join("%s" % valname for valname, value, helpstr in iter_allowed_values(allowed_values))

	elif allowed_values in PATTERNS:
		return PATTERNS[allowed_values]

	if not isinstance(allowed_values, str):
		allowed_values = allowed_values.__name__
	return "<%s>" % allowed_values

def label_allowed_values(allowed_values):
	if isinstance(allowed_values, (tuple, list)):
		if allowed_values[0] == list:
			assert len(allowed_values) == 2
			if isinstance(allowed_values[1], (tuple, list)):
				return _("A comma separated list which may contain the following values")
			else:
				return _("A comma separated list with data type")
		else:
			return _("Allowed values")
	elif allowed_values in PATTERNS:
		return _("Pattern")
	else:
		return _("Data type")

def format_value(value, allowed_values):
	if isinstance(allowed_values, (tuple, list)):
		if allowed_values[0] == list:
			return ",".join(format_value(v, allowed_values[1]) for v in value)

		for itervalname, itervalue, iterhelpstr in iter_allowed_values(allowed_values):
			if itervalue == value:
				return itervalname
		return repr(value)

	elif allowed_values == TYPE_COMMAND:
		if isinstance(value[0], str):
			value = [value]
		return '; '.join(shlex_join(cmd) for cmd in value)

	return str(value)

def can_be_true(allowed_values):
	if not isinstance(allowed_values, (tuple, list)):
		return False
	for valname, value, helpstr in iter_allowed_values(allowed_values):
		if valname == BOOL_TRUE:
			return True
	return False


def rgetattr(obj, name):
	if ATTR_SEP in name:
		n1, n2 = name.split(ATTR_SEP, 1)
		return rgetattr(getattr(obj, n1), n2)
	else:
		return getattr(obj, name)

def rsetattr(obj, name, value):
	if ATTR_SEP in name:
		n1, n2 = name.split(ATTR_SEP, 1)
		rsetattr(getattr(obj, n1), n2, value)
	elif hasattr(obj, name):
		setattr(obj, name, value)
	else:
		raise AttributeError("%s does not have attribute %s" % (obj, name))


def shlex_join(cmd):
	# this function is intended to be equivalent to shlex.join
	# I am not using shlex.join for backward compatibility with Python < 3.8
	# https://docs.python.org/3/library/shlex.html#shlex.join
	return " ".join(shlex.quote(w) for w in cmd)
