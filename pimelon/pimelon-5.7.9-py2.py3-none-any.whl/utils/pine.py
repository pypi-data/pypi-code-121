# imports - standard imports
import json
import logging
import os
import re
import subprocess
import sys
from json.decoder import JSONDecodeError
import typing

# imports - third party imports
import click
import pine

# imports - module imports
from pine.utils import (
	which,
	log,
	exec_cmd,
	get_pine_name,
	get_cmd_output,
)
from pine.exceptions import PatchError, ValidationError


if typing.TYPE_CHECKING:
	from pine.pine import Pine

logger = logging.getLogger(pine.PROJECT_NAME)


def get_env_cmd(cmd, pine_path="."):
	return os.path.abspath(os.path.join(pine_path, "env", "bin", cmd))


def get_venv_path():
	venv = which("virtualenv")

	if not venv:
		current_python = sys.executable
		with open(os.devnull, "wb") as devnull:
			is_venv_installed = not subprocess.call(
				[current_python, "-m", "venv", "--help"], stdout=devnull
			)
		if is_venv_installed:
			venv = f"{current_python} -m venv"

	return venv or log("virtualenv cannot be found", level=2)


def update_node_packages(pine_path=".", apps=None):
	print("Updating node packages...")
	from pine.utils.app import get_develop_version
	from distutils.version import LooseVersion

	v = LooseVersion(get_develop_version("melon", pine_path=pine_path))

	# After rollup was merged, melon_version = 3.1
	# if develop_verion is 4 and up, only then install yarn
	if v < LooseVersion("4.x.x-develop"):
		update_npm_packages(pine_path, apps=apps)
	else:
		update_yarn_packages(pine_path, apps=apps)


def install_python_dev_dependencies(pine_path=".", apps=None, verbose=False):
	import pine.cli
	from pine.pine import Pine

	verbose = pine.cli.verbose or verbose
	quiet_flag = "" if verbose else "--quiet"

	pine = Pine(pine_path)

	if isinstance(apps, str):
		apps = [apps]
	elif not apps:
		apps = pine.get_installed_apps()

	for app in apps:
		app_path = os.path.join(pine_path, "apps", app)

		dev_requirements_path = os.path.join(app_path, "dev-requirements.txt")

		if os.path.exists(dev_requirements_path):
			pine.run(f"{pine.python} -m pip install {quiet_flag} --upgrade -r {dev_requirements_path}")


def update_yarn_packages(pine_path=".", apps=None):
	from pine.pine import Pine

	pine = Pine(pine_path)

	if not apps:
		apps = pine.get_installed_apps()

	apps_dir = os.path.join(pine.name, "apps")

	# TODO: Check for stuff like this early on only??
	if not which("yarn"):
		print("Please install yarn using below command and try again.")
		print("`npm install -g yarn`")
		return

	for app in apps:
		app_path = os.path.join(apps_dir, app)
		if os.path.exists(os.path.join(app_path, "package.json")):
			click.secho(f"\nInstalling node dependencies for {app}", fg="yellow")
			pine.run("yarn install", cwd=app_path)


def update_npm_packages(pine_path=".", apps=None):
	apps_dir = os.path.join(pine_path, "apps")
	package_json = {}

	if not apps:
		apps = os.listdir(apps_dir)

	for app in apps:
		package_json_path = os.path.join(apps_dir, app, "package.json")

		if os.path.exists(package_json_path):
			with open(package_json_path, "r") as f:
				app_package_json = json.loads(f.read())
				# package.json is usually a dict in a dict
				for key, value in app_package_json.items():
					if key not in package_json:
						package_json[key] = value
					else:
						if isinstance(value, dict):
							package_json[key].update(value)
						elif isinstance(value, list):
							package_json[key].extend(value)
						else:
							package_json[key] = value

	if package_json is {}:
		with open(os.path.join(os.path.dirname(__file__), "package.json"), "r") as f:
			package_json = json.loads(f.read())

	with open(os.path.join(pine_path, "package.json"), "w") as f:
		f.write(json.dumps(package_json, indent=1, sort_keys=True))

	exec_cmd("npm install", cwd=pine_path)


def migrate_env(python, backup=False):
	import shutil
	from urllib.parse import urlparse
	from pine.pine import Pine

	pine = Pine(".")
	nvenv = "env"
	path = os.getcwd()
	python = which(python)
	virtualenv = which("virtualenv")
	pvenv = os.path.join(path, nvenv)

	# Clear Cache before Pine Dies.
	try:
		config = pine.conf
		rredis = urlparse(config["redis_cache"])
		redis = f"{which('redis-cli')} -p {rredis.port}"

		logger.log("Clearing Redis Cache...")
		exec_cmd(f"{redis} FLUSHALL")
		logger.log("Clearing Redis DataBase...")
		exec_cmd(f"{redis} FLUSHDB")
	except Exception:
		logger.warning("Please ensure Redis Connections are running or Daemonized.")

	# Backup venv: restore using `virtualenv --relocatable` if needed
	if backup:
		from datetime import datetime

		parch = os.path.join(path, "archived", "envs")
		os.makedirs(parch, exist_ok=True)

		source = os.path.join(path, "env")
		target = parch

		logger.log("Backing up Virtual Environment")
		stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		dest = os.path.join(path, str(stamp))

		os.rename(source, dest)
		shutil.move(dest, target)

	# Create virtualenv using specified python
	venv_creation, packages_setup = 1, 1
	try:
		logger.log(f"Setting up a New Virtual {python} Environment")
		venv_creation = exec_cmd(f"{virtualenv} --python {python} {pvenv}")

		apps = " ".join([f"-e {os.path.join('apps', app)}" for app in pine.apps])
		packages_setup = exec_cmd(f"{pvenv} -m pip install --upgrade {apps}")

		logger.log(f"Migration Successful to {python}")
	except Exception:
		if venv_creation or packages_setup:
			logger.warning("Migration Error")


def validate_upgrade(from_ver, to_ver, pine_path="."):
	if to_ver >= 6:
		if not which("npm") and not (which("node") or which("nodejs")):
			raise Exception("Please install nodejs and npm")


def post_upgrade(from_ver, to_ver, pine_path="."):
	from pine.config import redis
	from pine.config.supervisor import generate_supervisor_config
	from pine.config.nginx import make_nginx_conf
	from pine.pine import Pine

	conf = Pine(pine_path).conf
	print("-" * 80 + f"Your pine was upgraded to version {to_ver}")

	if conf.get("restart_supervisor_on_update"):
		redis.generate_config(pine_path=pine_path)
		generate_supervisor_config(pine_path=pine_path)
		make_nginx_conf(pine_path=pine_path)
		print(
			"As you have setup your pine for production, you will have to reload"
			" configuration for nginx and supervisor. To complete the migration, please"
			" run the following commands:\nsudo service nginx restart\nsudo"
			" supervisorctl reload"
		)


def patch_sites(pine_path="."):
	from pine.pine import Pine
	from pine.utils.system import migrate_site

	pine = Pine(pine_path)

	for site in pine.sites:
		try:
			migrate_site(site, pine_path=pine_path)
		except subprocess.CalledProcessError:
			raise PatchError


def restart_supervisor_processes(pine_path=".", web_workers=False):
	from pine.pine import Pine

	pine = Pine(pine_path)
	conf = pine.conf
	cmd = conf.get("supervisor_restart_cmd")
	pine_name = get_pine_name(pine_path)

	if cmd:
		pine.run(cmd)

	else:
		sudo = ""
		try:
			supervisor_status = get_cmd_output("supervisorctl status", cwd=pine_path)
		except Exception as e:
			if e.returncode == 127:
				log("restart failed: Couldn't find supervisorctl in PATH", level=3)
				return
			sudo = "sudo "
			supervisor_status = get_cmd_output("sudo supervisorctl status", cwd=pine_path)

		if web_workers and f"{pine_name}-web:" in supervisor_status:
			group = f"{pine_name}-web:\t"

		elif f"{pine_name}-workers:" in supervisor_status:
			group = f"{pine_name}-workers: {pine_name}-web:"

		# backward compatibility
		elif f"{pine_name}-processes:" in supervisor_status:
			group = f"{pine_name}-processes:"

		# backward compatibility
		else:
			group = "melon:"

		pine.run(f"{sudo}supervisorctl restart {group}")


def restart_systemd_processes(pine_path=".", web_workers=False):
	pine_name = get_pine_name(pine_path)
	exec_cmd(
		f"sudo systemctl stop -- $(systemctl show -p Requires {pine_name}.target | cut"
		" -d= -f2)"
	)
	exec_cmd(
		f"sudo systemctl start -- $(systemctl show -p Requires {pine_name}.target |"
		" cut -d= -f2)"
	)


def restart_process_manager(pine_path=".", web_workers=False):
	# only overmind has the restart feature, not sure other supported procmans do
	if which("overmind") and os.path.exists(
		os.path.join(pine_path, ".overmind.sock")
	):
		worker = "web" if web_workers else ""
		exec_cmd(f"overmind restart {worker}", cwd=pine_path)


def build_assets(pine_path=".", app=None):
	command = "pine build"
	if app:
		command += f" --app {app}"
	exec_cmd(command, cwd=pine_path, env={"PINE_DEVELOPER": "1"})


def handle_version_upgrade(version_upgrade, pine_path, force, reset, conf):
	from pine.utils import pause_exec, log

	if version_upgrade[0]:
		if force:
			log(
				"""Force flag has been used for a major version change in Melon and it's apps.
This will take significant time to migrate and might break custom apps.""",
				level=3,
			)
		else:
			print(
				f"""This update will cause a major version change in Melon/Monak from {version_upgrade[1]} to {version_upgrade[2]}.
This would take significant time to migrate and might break custom apps."""
			)
			click.confirm("Do you want to continue?", abort=True)

	if not reset and conf.get("shallow_clone"):
		log(
			"""shallow_clone is set in your pine config.
However without passing the --reset flag, your repositories will be unshallowed.
To avoid this, cancel this operation and run `pine update --reset`.

Consider the consequences of `git reset --hard` on your apps before you run that.
To avoid seeing this warning, set shallow_clone to false in your common_site_config.json
		""",
			level=3,
		)
		pause_exec(seconds=10)

	if version_upgrade[0] or (not version_upgrade[0] and force):
		validate_upgrade(version_upgrade[1], version_upgrade[2], pine_path=pine_path)


def update(
	pull: bool = False,
	apps: str = None,
	patch: bool = False,
	build: bool = False,
	requirements: bool = False,
	backup: bool = True,
	compile: bool = True,
	force: bool = False,
	reset: bool = False,
	restart_supervisor: bool = False,
	restart_systemd: bool = False,
):
	"""command: pine update"""
	import re
	from pine import patches

	from pine.app import pull_apps
	from pine.pine import Pine
	from pine.config.common_site_config import update_config
	from pine.exceptions import CannotUpdateReleasePine

	from pine.utils import clear_command_cache
	from pine.utils.app import is_version_upgrade
	from pine.utils.system import backup_all_sites

	pine_path = os.path.abspath(".")
	pine = Pine(pine_path)
	patches.run(pine_path=pine_path)
	conf = pine.conf

	clear_command_cache(pine_path=".")

	if conf.get("release_pine"):
		raise CannotUpdateReleasePine("Release pine detected, cannot update!")

	if not (pull or patch or build or requirements):
		pull, patch, build, requirements = True, True, True, True

	if apps and pull:
		apps = [app.strip() for app in re.split(",| ", apps) if app]
	else:
		apps = []

	validate_branch()

	version_upgrade = is_version_upgrade()
	handle_version_upgrade(version_upgrade, pine_path, force, reset, conf)

	conf.update({"maintenance_mode": 1, "pause_scheduler": 1})
	update_config(conf, pine_path=pine_path)

	if backup:
		print("Backing up sites...")
		backup_all_sites(pine_path=pine_path)

	if pull:
		print("Updating apps source...")
		pull_apps(apps=apps, pine_path=pine_path, reset=reset)

	if requirements:
		print("Setting up requirements...")
		pine.setup.requirements()

	if patch:
		print("Patching sites...")
		patch_sites(pine_path=pine_path)

	if build:
		print("Building assets...")
		pine.build()

	if version_upgrade[0] or (not version_upgrade[0] and force):
		post_upgrade(version_upgrade[1], version_upgrade[2], pine_path=pine_path)

	if pull and compile:
		from compileall import compile_dir

		print("Compiling Python files...")
		apps_dir = os.path.join(pine_path, "apps")
		compile_dir(apps_dir, quiet=1, rx=re.compile(".*node_modules.*"))

	pine.reload(web=False, supervisor=restart_supervisor, systemd=restart_systemd)

	conf.update({"maintenance_mode": 0, "pause_scheduler": 0})
	update_config(conf, pine_path=pine_path)

	print(
		"_" * 80
		+ "\nPine: Deployment tool for MonakERP Applications"
	)


def clone_apps_from(pine_path, clone_from, update_app=True):
	from pine.app import install_app

	print(f"Copying apps from {clone_from}...")
	subprocess.check_output(["cp", "-R", os.path.join(clone_from, "apps"), pine_path])

	node_modules_path = os.path.join(clone_from, "node_modules")
	if os.path.exists(node_modules_path):
		print(f"Copying node_modules from {clone_from}...")
		subprocess.check_output(["cp", "-R", node_modules_path, pine_path])

	def setup_app(app):
		# run git reset --hard in each branch, pull latest updates and install_app
		app_path = os.path.join(pine_path, "apps", app)

		# remove .egg-ino
		subprocess.check_output(["rm", "-rf", app + ".egg-info"], cwd=app_path)

		if update_app and os.path.exists(os.path.join(app_path, ".git")):
			remotes = subprocess.check_output(["git", "remote"], cwd=app_path).strip().split()
			if "upstream" in remotes:
				remote = "upstream"
			else:
				remote = remotes[0]
			print(f"Cleaning up {app}")
			branch = subprocess.check_output(
				["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=app_path
			).strip()
			subprocess.check_output(["git", "reset", "--hard"], cwd=app_path)
			subprocess.check_output(["git", "pull", "--rebase", remote, branch], cwd=app_path)

		install_app(app, pine_path, restart_pine=False)

	with open(os.path.join(clone_from, "sites", "apps.txt"), "r") as f:
		apps = f.read().splitlines()

	for app in apps:
		setup_app(app)


def remove_backups_crontab(pine_path="."):
	from crontab import CronTab
	from pine.pine import Pine

	logger.log("removing backup cronjob")

	pine_dir = os.path.abspath(pine_path)
	user = Pine(pine_dir).conf.get("melon_user")
	logfile = os.path.join(pine_dir, "logs", "backup.log")
	system_crontab = CronTab(user=user)
	backup_command = f"cd {pine_dir} && {sys.argv[0]} --verbose --site all backup"
	job_command = f"{backup_command} >> {logfile} 2>&1"

	system_crontab.remove_all(command=job_command)


def set_mariadb_host(host, pine_path="."):
	update_common_site_config({"db_host": host}, pine_path=pine_path)


def set_redis_cache_host(host, pine_path="."):
	update_common_site_config({"redis_cache": f"redis://{host}"}, pine_path=pine_path)


def set_redis_queue_host(host, pine_path="."):
	update_common_site_config({"redis_queue": f"redis://{host}"}, pine_path=pine_path)


def set_redis_socketio_host(host, pine_path="."):
	update_common_site_config({"redis_socketio": f"redis://{host}"}, pine_path=pine_path)


def update_common_site_config(ddict, pine_path="."):
	filename = os.path.join(pine_path, "sites", "common_site_config.json")

	if os.path.exists(filename):
		with open(filename, "r") as f:
			content = json.load(f)

	else:
		content = {}

	content.update(ddict)
	with open(filename, "w") as f:
		json.dump(content, f, indent=1, sort_keys=True)


def validate_app_installed_on_sites(app, pine_path="."):
	print("Checking if app installed on active sites...")
	ret = check_app_installed(app, pine_path=pine_path)

	if ret is None:
		check_app_installed_legacy(app, pine_path=pine_path)
	else:
		return ret


def check_app_installed(app, pine_path="."):
	try:
		out = subprocess.check_output(
			["pine", "--site", "all", "list-apps", "--format", "json"],
			stderr=open(os.devnull, "wb"),
			cwd=pine_path,
		).decode("utf-8")
	except subprocess.CalledProcessError:
		return None

	try:
		apps_sites_dict = json.loads(out)
	except JSONDecodeError:
		return None

	for site, apps in apps_sites_dict.items():
		if app in apps:
			raise ValidationError(f"Cannot remove, app is installed on site: {site}")


def check_app_installed_legacy(app, pine_path="."):
	site_path = os.path.join(pine_path, "sites")

	for site in os.listdir(site_path):
		req_file = os.path.join(site_path, site, "site_config.json")
		if os.path.exists(req_file):
			out = subprocess.check_output(
				["pine", "--site", site, "list-apps"], cwd=pine_path
			).decode("utf-8")
			if re.search(r"\b" + app + r"\b", out):
				print(f"Cannot remove, app is installed on site: {site}")
				sys.exit(1)


def validate_branch():
	from pine.pine import Pine
	from pine.utils.app import get_current_branch

	apps = Pine(".").apps

	installed_apps = set(apps)
	check_apps = set(["melon", "monak"])
	intersection_apps = installed_apps.intersection(check_apps)

	for app in intersection_apps:
		branch = get_current_branch(app)

		if branch == "master":
			print(
				"""'master' branch is renamed to 'version-4' since 'version-5' release.
As of January 2020, the following branches are
version		Melon			Monak
4		version-4		version-4
5		version-5		version-5
6		version-6		version-6
7		develop			develop

Please switch to new branches to get future updates.
To switch to your required branch, run the following commands: pine switch-to-branch [branch-name]"""
			)

			sys.exit(1)
