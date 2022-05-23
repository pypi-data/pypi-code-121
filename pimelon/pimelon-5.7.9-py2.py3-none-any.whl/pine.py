# imports - standard imports
import functools
import os
import shutil
import sys
import logging
from typing import List, MutableSequence, TYPE_CHECKING

# imports - module imports
import pine
from pine.exceptions import ValidationError
from pine.config.common_site_config import setup_config
from pine.utils import (
	paths_in_pine,
	exec_cmd,
	is_pine_directory,
	is_melon_app,
	get_cmd_output,
	get_git_version,
	log,
	run_melon_cmd,
)
from pine.utils.pine import (
	validate_app_installed_on_sites,
	restart_supervisor_processes,
	restart_systemd_processes,
	restart_process_manager,
	remove_backups_crontab,
	get_venv_path,
	get_env_cmd,
)
from pine.utils.render import job, step


if TYPE_CHECKING:
	from pine.app import App

logger = logging.getLogger(pine.PROJECT_NAME)


class Base:
	def run(self, cmd, cwd=None):
		return exec_cmd(cmd, cwd=cwd or self.cwd)


class Validator:
	def validate_app_uninstall(self, app):
		if app not in self.apps:
			raise ValidationError(f"No app named {app}")
		validate_app_installed_on_sites(app, pine_path=self.name)


@functools.lru_cache(maxsize=None)
class Pine(Base, Validator):
	def __init__(self, path):
		self.name = path
		self.cwd = os.path.abspath(path)
		self.exists = is_pine_directory(self.name)

		self.setup = PineSetup(self)
		self.teardown = PineTearDown(self)
		self.apps = PineApps(self)

		self.apps_txt = os.path.join(self.name, "sites", "apps.txt")
		self.excluded_apps_txt = os.path.join(self.name, "sites", "excluded_apps.txt")

	@property
	def python(self) -> str:
		return get_env_cmd("python", pine_path=self.name)

	@property
	def shallow_clone(self) -> bool:
		config = self.conf

		if config:
			if config.get("release_pine") or not config.get("shallow_clone"):
				return False

		return get_git_version() > 1.9

	@property
	def excluded_apps(self) -> List:
		try:
			with open(self.excluded_apps_txt) as f:
				return f.read().strip().split("\n")
		except Exception:
			return []

	@property
	def sites(self) -> List:
		return [
			path
			for path in os.listdir(os.path.join(self.name, "sites"))
			if os.path.exists(os.path.join("sites", path, "site_config.json"))
		]

	@property
	def conf(self):
		from pine.config.common_site_config import get_config

		return get_config(self.name)

	def init(self):
		self.setup.dirs()
		self.setup.env()
		self.setup.backups()

	def drop(self):
		self.teardown.backups()
		self.teardown.dirs()

	def install(self, app, branch=None):
		from pine.app import App

		app = App(app, branch=branch)
		self.apps.append(app)
		self.apps.sync()

	def uninstall(self, app):
		from pine.app import App

		self.validate_app_uninstall(app)
		self.apps.remove(App(app, pine=self, to_clone=False))
		self.apps.sync()
		# self.build() - removed because it seems unnecessary
		self.reload()

	@step(title="Building Pine Assets", success="Pine Assets Built")
	def build(self):
		# build assets & stuff
		run_melon_cmd("build", pine_path=self.name)

	@step(title="Reloading Pine Processes", success="Pine Processes Reloaded")
	def reload(self, web=False, supervisor=True, systemd=True):
		"""If web is True, only web workers are restarted
		"""
		conf = self.conf

		if conf.get("developer_mode"):
			restart_process_manager(pine_path=self.name, web_workers=web)
		if supervisor and conf.get("restart_supervisor_on_update"):
			restart_supervisor_processes(pine_path=self.name, web_workers=web)
		if systemd and conf.get("restart_systemd_on_update"):
			restart_systemd_processes(pine_path=self.name, web_workers=web)

	def get_installed_apps(self) -> List:
		"""Returns list of installed apps on pine, not in excluded_apps.txt
		"""
		apps = [app for app in self.apps if app not in self.excluded_apps]
		apps.remove("melon")
		apps.insert(0, "melon")
		return apps


class PineApps(MutableSequence):
	def __init__(self, pine: Pine):
		self.pine = pine
		self.initialize_apps()

	def sync(self):
		self.initialize_apps()
		with open(self.pine.apps_txt, "w") as f:
			return f.write("\n".join(self.apps))

	def initialize_apps(self):
		is_installed = lambda app: app in installed_packages

		try:
			installed_packages = get_cmd_output(f"{self.pine.python} -m pip freeze", cwd=self.pine.name)
		except Exception:
			self.apps = []
			return

		try:
			self.apps = [
				x
				for x in os.listdir(os.path.join(self.pine.name, "apps"))
				if (
					is_melon_app(os.path.join(self.pine.name, "apps", x))
					and is_installed(x)
				)
			]
			self.apps.sort()
		except FileNotFoundError:
			self.apps = []

	def __getitem__(self, key):
		""" retrieves an item by its index, key"""
		return self.apps[key]

	def __setitem__(self, key, value):
		""" set the item at index, key, to value """
		# should probably not be allowed
		# self.apps[key] = value
		raise NotImplementedError

	def __delitem__(self, key):
		""" removes the item at index, key """
		# TODO: uninstall and delete app from pine
		del self.apps[key]

	def __len__(self):
		return len(self.apps)

	def insert(self, key, value):
		""" add an item, value, at index, key. """
		# TODO: fetch and install app to pine
		self.apps.insert(key, value)

	def add(self, app: "App"):
		app.get()
		app.install()
		super().append(app.repo)
		self.apps.sort()

	def remove(self, app: "App"):
		app.uninstall()
		app.remove()
		super().remove(app.repo)

	def append(self, app: "App"):
		return self.add(app)

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return str([x for x in self.apps])


class PineSetup(Base):
	def __init__(self, pine: Pine):
		self.pine = pine
		self.cwd = self.pine.cwd

	@step(title="Setting Up Directories", success="Directories Set Up")
	def dirs(self):
		os.makedirs(self.pine.name, exist_ok=True)

		for dirname in paths_in_pine:
			os.makedirs(os.path.join(self.pine.name, dirname), exist_ok=True)

	@step(title="Setting Up Environment", success="Environment Set Up")
	def env(self, python="python3"):
		"""Setup env folder
		- create env if not exists
		- upgrade env pip
		- install melon python dependencies
		"""
		import pine.cli

		melon = os.path.join(self.pine.name, "apps", "melon")
		virtualenv = get_venv_path()
		quiet_flag = "" if pine.cli.verbose else "--quiet"

		if not os.path.exists(self.pine.python):
			self.run(f"{virtualenv} {quiet_flag} env -p {python}")

		self.pip()

		if os.path.exists(melon):
			self.run(f"{self.pine.python} -m pip install {quiet_flag} --upgrade -e {melon}")

	@step(title="Setting Up Pine Config", success="Pine Config Set Up")
	def config(self, redis=True, procfile=True):
		"""Setup config folder
		- create pids folder
		- generate sites/common_site_config.json
		"""
		setup_config(self.pine.name)

		if redis:
			from pine.config.redis import generate_config

			generate_config(self.pine.name)

		if procfile:
			from pine.config.procfile import setup_procfile

			setup_procfile(self.pine.name, skip_redis=not redis)

	@step(title="Updating pip", success="Updated pip")
	def pip(self, verbose=False):
		"""Updates env pip; assumes that env is setup
		"""
		import pine.cli

		verbose = pine.cli.verbose or verbose
		quiet_flag = "" if verbose else "--quiet"

		return self.run(f"{self.pine.python} -m pip install {quiet_flag} --upgrade pip")

	def logging(self):
		from pine.utils import setup_logging

		return setup_logging(pine_path=self.pine.name)

	@step(title="Setting Up Pine Patches", success="Pine Patches Set Up")
	def patches(self):
		shutil.copy(
			os.path.join(os.path.dirname(os.path.abspath(__file__)), "patches", "patches.txt"),
			os.path.join(self.pine.name, "patches.txt"),
		)

	@step(title="Setting Up Backups Cronjob", success="Backups Cronjob Set Up")
	def backups(self):
		# TODO: to something better for logging data? - maybe a wrapper that auto-logs with more context
		logger.log("setting up backups")

		from crontab import CronTab

		pine_dir = os.path.abspath(self.pine.name)
		user = self.pine.conf.get("melon_user")
		logfile = os.path.join(pine_dir, "logs", "backup.log")
		system_crontab = CronTab(user=user)
		backup_command = f"cd {pine_dir} && {sys.argv[0]} --verbose --site all backup"
		job_command = f"{backup_command} >> {logfile} 2>&1"

		if job_command not in str(system_crontab):
			job = system_crontab.new(
				command=job_command, comment="pine auto backups set for every 12 hours"
			)
			job.every(12).hours()
			system_crontab.write()

		logger.log("backups were set up")

	@job(title="Setting Up Pine Dependencies", success="Pine Dependencies Set Up")
	def requirements(self, apps=None):
		"""Install and upgrade specified / all installed apps on given Pine
		"""
		from pine.app import App

		if not apps:
			apps = self.pine.get_installed_apps()

		self.pip()

		print(f"Installing {len(apps)} applications...")

		for app in apps:
			App(app, pine=self.pine, to_clone=False).install( skip_assets=True, restart_pine=False)

	def python(self, apps=None):
		"""Install and upgrade Python dependencies for specified / all installed apps on given Pine
		"""
		import pine.cli

		if not apps:
			apps = self.pine.get_installed_apps()

		quiet_flag = "" if pine.cli.verbose else "--quiet"

		self.pip()

		for app in apps:
			app_path = os.path.join(self.pine.name, "apps", app)
			log(f"\nInstalling python dependencies for {app}", level=3, no_log=True)
			self.run(f"{self.pine.python} -m pip install {quiet_flag} --upgrade -e {app_path}")

	def node(self, apps=None):
		"""Install and upgrade Node dependencies for specified / all apps on given Pine
		"""
		from pine.utils.pine import update_node_packages

		return update_node_packages(pine_path=self.pine.name, apps=apps)


class PineTearDown:
	def __init__(self, pine):
		self.pine = pine

	def backups(self):
		remove_backups_crontab(self.pine.name)

	def dirs(self):
		shutil.rmtree(self.pine.name)
