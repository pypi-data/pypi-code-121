# imports - standard imports
import grp
import os
import pwd
import shutil
import sys

# imports - module imports
import pine
from pine.utils import (
	exec_cmd,
	get_process_manager,
	log,
	run_melon_cmd,
	sudoers_file,
	which,
)
from pine.utils.pine import build_assets, clone_apps_from
from pine.utils.render import job


@job(title="Initializing Pine {path}", success="Pine {path} initialized")
def init(
	path,
	apps_path=None,
	no_procfile=False,
	no_backups=False,
	melon_path=None,
	melon_branch=None,
	verbose=False,
	clone_from=None,
	skip_redis_config_generation=False,
	clone_without_update=False,
	skip_assets=False,
	python="python3",
	install_app=None,
):
	"""Initialize a new pine directory

	* create a pine directory in the given path
	* setup logging for the pine
	* setup env for the pine
	* setup config (dir/pids/redis/procfile) for the pine
	* setup patches.txt for pine
	* clone & install melon
		* install python & node dependencies
		* build assets
	* setup backups crontab
	"""

	# Use print("\033c", end="") to clear entire screen after each step and re-render each list
	# another way => https://stackoverflow.com/a/44591228/10309266

	import pine.cli
	from pine.app import get_app, install_apps_from_path
	from pine.pine import Pine

	verbose = pine.cli.verbose or verbose

	pine = Pine(path)

	pine.setup.dirs()
	pine.setup.logging()
	pine.setup.env(python=python)
	pine.setup.config(redis=not skip_redis_config_generation, procfile=not no_procfile)
	pine.setup.patches()

	# local apps
	if clone_from:
		clone_apps_from(
			pine_path=path, clone_from=clone_from, update_app=not clone_without_update
		)

	# remote apps
	else:
		melon_path = melon_path or "https://github.com/amonak/melon.git"

		get_app(
			melon_path, branch=melon_branch, pine_path=path, skip_assets=True, verbose=verbose
		)

		# fetch remote apps using config file - deprecate this!
		if apps_path:
			install_apps_from_path(apps_path, pine_path=path)

	# getting app on pine init using --install-app
	if install_app:
		get_app(
			install_app, branch=melon_branch, pine_path=path, skip_assets=True, verbose=verbose
		)

	if not skip_assets:
		build_assets(pine_path=path)

	if not no_backups:
		pine.setup.backups()


def setup_sudoers(user):
	if not os.path.exists("/etc/sudoers.d"):
		os.makedirs("/etc/sudoers.d")

		set_permissions = False
		if not os.path.exists("/etc/sudoers"):
			set_permissions = True

		with open("/etc/sudoers", "a") as f:
			f.write("\n#includedir /etc/sudoers.d\n")

		if set_permissions:
			os.chmod("/etc/sudoers", 0o440)

	template = pine.config.env().get_template("melon_sudoers")
	melon_sudoers = template.render(
		**{
			"user": user,
			"service": which("service"),
			"systemctl": which("systemctl"),
			"nginx": which("nginx"),
		}
	)

	with open(sudoers_file, "w") as f:
		f.write(melon_sudoers)

	os.chmod(sudoers_file, 0o440)
	log(f"Sudoers was set up for user {user}", level=1)


def start(no_dev=False, concurrency=None, procfile=None, no_prefix=False, procman=None):
	if procman:
		program = which(procman)
	else:
		program = get_process_manager()

	if not program:
		raise Exception("No process manager found")

	os.environ["PYTHONUNBUFFERED"] = "true"
	if not no_dev:
		os.environ["DEV_SERVER"] = "true"

	command = [program, "start"]
	if concurrency:
		command.extend(["-c", concurrency])

	if procfile:
		command.extend(["-f", procfile])

	if no_prefix:
		command.extend(["--no-prefix"])

	os.execv(program, command)


def migrate_site(site, pine_path="."):
	run_melon_cmd("--site", site, "migrate", pine_path=pine_path)


def backup_site(site, pine_path="."):
	run_melon_cmd("--site", site, "backup", pine_path=pine_path)


def backup_all_sites(pine_path="."):
	from pine.pine import Pine

	for site in Pine(pine_path).sites:
		backup_site(site, pine_path=pine_path)


def fix_prod_setup_perms(pine_path=".", melon_user=None):
	from glob import glob
	from pine.pine import Pine

	melon_user = melon_user or Pine(pine_path).conf.get("melon_user")

	if not melon_user:
		print("melon user not set")
		sys.exit(1)

	globs = ["logs/*", "config/*"]
	for glob_name in globs:
		for path in glob(glob_name):
			uid = pwd.getpwnam(melon_user).pw_uid
			gid = grp.getgrnam(melon_user).gr_gid
			os.chown(path, uid, gid)


def setup_fonts():
	fonts_path = os.path.join("/tmp", "fonts")

	if os.path.exists("/etc/fonts_backup"):
		return

	exec_cmd("git clone https://github.com/amonak/fonts.git", cwd="/tmp")
	os.rename("/etc/fonts", "/etc/fonts_backup")
	os.rename("/usr/share/fonts", "/usr/share/fonts_backup")
	os.rename(os.path.join(fonts_path, "etc_fonts"), "/etc/fonts")
	os.rename(os.path.join(fonts_path, "usr_share_fonts"), "/usr/share/fonts")
	shutil.rmtree(fonts_path)
	exec_cmd("fc-cache -fv")
