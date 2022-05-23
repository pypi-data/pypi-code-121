# imports - standard imports
import atexit
import json
import os
import pwd
import sys

# imports - third party imports
import click

# imports - module imports
import pine
from pine.pine import Pine
from pine.commands import pine_command
from pine.config.common_site_config import get_config
from pine.utils import (
	pine_cache_file,
	check_latest_version,
	drop_privileges,
	find_parent_pine,
	generate_command_cache,
	get_cmd_output,
	is_pine_directory,
	is_dist_editable,
	is_root,
	log,
	setup_logging,
	parse_sys_argv,
)
from pine.utils.pine import get_env_cmd

# these variables are used to show dynamic outputs on the terminal
dynamic_feed = False
verbose = False
is_envvar_warn_set = None
from_command_line = False # set when commands are executed via the CLI
pine.LOG_BUFFER = []
sys_argv = None

change_uid_msg = "You should not run this command as root"
src = os.path.dirname(__file__)


def cli():
	global from_command_line, pine_config, is_envvar_warn_set, verbose, sys_argv

	from_command_line = True
	command = " ".join(sys.argv)
	argv = set(sys.argv)
	is_envvar_warn_set = not (os.environ.get("PINE_DEVELOPER") or os.environ.get("CI"))
	is_cli_command = len(sys.argv) > 1 and not argv.intersection({"src", "--version"})
	sys_argv = parse_sys_argv()

	if "--verbose" in sys_argv.options:
		verbose = True

	change_working_directory()
	logger = setup_logging()
	logger.info(command)
	setup_clear_cache()

	pine_config = get_config(".")

	if is_cli_command:
		check_uid()
		change_uid()
		change_dir()

	if (
		is_envvar_warn_set
		and is_cli_command
		and is_dist_editable(pine.PROJECT_NAME)
		and not pine_config.get("developer_mode")
	):
		log(
			"pine is installed in editable mode!\n\nThis is not the recommended mode"
			" of installation for production. Instead, install the package from PyPI"
			" with: `pip install pimelon`\n",
			level=3,
		)

	in_pine = is_pine_directory()

	if (
		not in_pine
		and len(sys.argv) > 1
		and not argv.intersection({"init", "find", "src", "drop", "get", "get-app", "--version"})
		and not cmd_requires_root()
	):
		log("Command not being executed in pine directory", level=3)

	if in_pine and len(sys.argv) > 1:
		if sys.argv[1] == "--help":
			print(click.Context(pine_command).get_help())
			print(get_melon_help())
			return

		if (
			sys_argv.commands.intersection(get_cached_melon_commands())
			or sys_argv.commands.intersection(get_melon_commands())
		):
			melon_cmd()

		if sys.argv[1] in Pine(".").apps:
			app_cmd()

	if not is_cli_command:
		atexit.register(check_latest_version)

	try:
		pine_command()
	except BaseException as e:
		return_code = getattr(e, "code", 1)

		if isinstance(e, Exception):
			click.secho(f"ERROR: {e}", fg="red")

		if return_code:
			logger.warning(f"{command} executed with exit code {return_code}")

		raise e


def check_uid():
	if cmd_requires_root() and not is_root():
		log("superuser privileges required for this command", level=3)
		sys.exit(1)


def cmd_requires_root():
	if len(sys.argv) > 2 and sys.argv[2] in (
		"production",
		"sudoers",
		"lets-encrypt",
		"fonts",
		"print",
		"firewall",
		"ssh-port",
		"role",
		"fail2ban",
		"wildcard-ssl",
	):
		return True
	if len(sys.argv) >= 2 and sys.argv[1] in (
		"patch",
		"renew-lets-encrypt",
		"disable-production",
	):
		return True
	if len(sys.argv) > 2 and sys.argv[1] in ("install"):
		return True


def change_dir():
	if os.path.exists("config.json") or "init" in sys.argv:
		return
	dir_path_file = "/etc/pimelon_dir"
	if os.path.exists(dir_path_file):
		with open(dir_path_file) as f:
			dir_path = f.read().strip()
		if os.path.exists(dir_path):
			os.chdir(dir_path)


def change_uid():
	if is_root() and not cmd_requires_root():
		melon_user = pine_config.get("melon_user")
		if melon_user:
			drop_privileges(uid_name=melon_user, gid_name=melon_user)
			os.environ["HOME"] = pwd.getpwnam(melon_user).pw_dir
		else:
			log(change_uid_msg, level=3)
			sys.exit(1)


def app_cmd(pine_path="."):
	f = get_env_cmd("python", pine_path=pine_path)
	os.chdir(os.path.join(pine_path, "sites"))
	os.execv(f, [f] + ["-m", "melon.utils.pine_helper"] + sys.argv[1:])


def melon_cmd(pine_path="."):
	f = get_env_cmd("python", pine_path=pine_path)
	os.chdir(os.path.join(pine_path, "sites"))
	os.execv(f, [f] + ["-m", "melon.utils.pine_helper", "melon"] + sys.argv[1:])


def get_cached_melon_commands():
	if os.path.exists(pine_cache_file):
		command_dump = open(pine_cache_file, "r").read() or "[]"
		return set(json.loads(command_dump))
	return set()


def get_melon_commands():
	if not is_pine_directory():
		return set()

	return set(generate_command_cache())


def get_melon_help(pine_path="."):
	python = get_env_cmd("python", pine_path=pine_path)
	sites_path = os.path.join(pine_path, "sites")
	try:
		out = get_cmd_output(
			f"{python} -m melon.utils.pine_helper get-melon-help", cwd=sites_path
		)
		return "\n\nFramework commands:\n" + out.split("Commands:")[1]
	except Exception:
		return ""


def change_working_directory():
	"""Allows pine commands to be run from anywhere inside a pine directory"""
	cur_dir = os.path.abspath(".")
	pine_path = find_parent_pine(cur_dir)
	pine.current_path = os.getcwd()
	pine.updated_path = pine_path

	if pine_path:
		os.chdir(pine_path)


def setup_clear_cache():
	from copy import copy
	f = copy(os.chdir)

	def _chdir(*args, **kwargs):
		Pine.cache_clear()
		return f(*args, **kwargs)

	os.chdir = _chdir
