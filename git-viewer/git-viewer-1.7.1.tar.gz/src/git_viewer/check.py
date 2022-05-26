#!/usr/bin/env python3

import os
import sys
import gettext
_ = gettext.gettext

from .api_subprocess import Runner, CommandError


EXIT_GIT_NOT_INSTALLED = 1
EXIT_NOT_A_REPO = 2

EXIT_PYTHON_TOO_OLD = 4


# ---------- current working directory ---------

def assert_git_repo():
	for arg in sys.argv[1:]:
		if arg.startswith('--git-dir'):
			return

	r = Runner()
	cmd = ["git", "rev-parse", "--is-inside-git-dir"]
	try:
		out = r.run_and_get_output(cmd)
	except CommandError as e:
		if e.executable_was_found():
			error(EXIT_NOT_A_REPO, _("The current working directory is not a git repository."))
		else:
			error(EXIT_GIT_NOT_INSTALLED, _("git is not installed."))

	out = out.rstrip()
	if out == "true":
		path = os.getcwd().split(os.sep)
		try:
			i = path.index('.git')
		except ValueError:
			error(EXIT_NOT_A_REPO, _("Failed to leave the .git directory."))
		repo_path = os.path.sep.join(path[:i])
		internal_path = path[i+1:]
		try:
			i = internal_path.index('modules')
		except ValueError:
			pass
		else:
			module_path = internal_path[i+1:]
			repo_path = os.path.join(repo_path, *module_path)

		os.chdir(repo_path)
		assert_git_repo()


# ---------- urwid version ---------

def check_urwid_version():
	if not is_urwid_new_enough_for_ellipsis(fallback=True):
		from . import urwid_text_layout
		urwid_text_layout.LogTextLayout.ALLOWED_WRAP_VALUES = tuple(wrap for wrap in urwid_text_layout.LogTextLayout.ALLOWED_WRAP_VALUES if wrap != urwid_text_layout.LogTextLayout.WRAP_ELLIPSIS)

def is_urwid_new_enough(version, fallback=True, assumption=None):
	try:
		from packaging import version
		import urwid
		return version.parse(urwid.__version__) >= version.parse("2.1.0")
	except ImportError:
		if assumption:
			warning(_("Failed to check urwid version because packaging is not installed. %s You can install packaging using `pip3 install --user packaging`." % assumption.strip()))
		return fallback

def is_urwid_new_enough_for_ellipsis(**kw):
	return is_urwid_new_enough('2.1.0', **kw)

def is_urwid_new_enough_for_explicit_spaces(**kw):
	return is_urwid_new_enough('2.1.0', **kw)


# ---------- python version ---------

def assert_python_new_enough():
	if sys.version_info <= (3, 5, 0):
		error(EXIT_PYTHON_TOO_OLD, _("This program requires at least Python 3.5.\nYou are using Python {version}.").format(version=sys.version.replace("\n", "")))


# ---------- main ---------

def warning(message):
	sys.stderr.write(message)
	sys.stderr.write("\n")

def error(error_number, error_message):
	sys.stderr.write(error_message)
	sys.stderr.write("\n")
	exit(error_number)

def run_all_checks():
	assert_python_new_enough()
	assert_git_repo()
	check_urwid_version()


if __name__ == '__main__':
	run_all_checks()
