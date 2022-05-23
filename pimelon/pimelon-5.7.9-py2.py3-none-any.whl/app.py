# imports - standard imports
import functools
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import typing
from datetime import date
from urllib.parse import urlparse

# imports - third party imports
import click

# imports - module imports
import pine
from pine.exceptions import NotInPineDirectoryError
from pine.utils import (
	fetch_details_from_tag,
	get_available_folder_name,
	is_pine_directory,
	is_git_url,
	log,
	run_melon_cmd,
)
from pine.utils.pine import (
	build_assets,
	install_python_dev_dependencies,
)
from pine.utils.render import step

if typing.TYPE_CHECKING:
	from pine.pine import Pine


logger = logging.getLogger(pine.PROJECT_NAME)


class AppMeta:
	def __init__(self, name: str, branch: str = None, to_clone: bool = True):
		"""
		name (str): This could look something like
			1. https://github.com/amonak/healthcare.git
			2. git@github.com:melon/healthcare.git
			3. melon/healthcare@develop
			4. healthcare
			5. healthcare@develop, healthcare@v6.12.1

		References for Version Identifiers:
		 * https://www.python.org/dev/peps/pep-0440/#version-specifiers
		 * https://docs.npmjs.com/about-semantic-versioning

		class Healthcare(AppConfig):
			dependencies = [{"melon/monak": "~6.17.0"}]
		"""
		self.name = name.rstrip('/')
		self.remote_server = "github.com"
		self.to_clone = to_clone
		self.on_disk = False
		self.use_ssh = False
		self.from_apps = False
		self.is_url = False
		self.branch = branch
		self.mount_path = os.path.abspath(
			os.path.join(urlparse(self.name).netloc, urlparse(self.name).path)
		)
		self.setup_details()

	def setup_details(self):
		# fetch meta from installed apps
		if (
			not self.to_clone
			and hasattr(self, "pine")
			and os.path.exists(os.path.join(self.pine.name, "apps", self.name))
		):
			self.from_apps = True
			self._setup_details_from_installed_apps()

		# fetch meta for repo on mounted disk
		elif os.path.exists(self.mount_path):
			self.on_disk = True
			self._setup_details_from_mounted_disk()

		# fetch meta for repo from remote git server - traditional get-app url
		elif is_git_url(self.name):
			self.is_url = True
			if self.name.startswith("git@") or self.name.startswith("ssh://"):
				self.use_ssh = True
			self._setup_details_from_git_url()

		# fetch meta from new styled name tags & first party apps on github
		else:
			self._setup_details_from_name_tag()

	def _setup_details_from_mounted_disk(self):
		self.org, self.repo, self.tag = os.path.split(self.mount_path)[-2:] + (
			self.branch,
		)

	def _setup_details_from_name_tag(self):
		self.org, self.repo, self.tag = fetch_details_from_tag(self.name)
		self.tag = self.tag or self.branch

	def _setup_details_from_installed_apps(self):
		self.org, self.repo, self.tag = os.path.split(
			os.path.join(self.pine.name, "apps", self.name)
		)[-2:] + (self.branch,)

	def _setup_details_from_git_url(self):
		return self.__setup_details_from_git()

	def __setup_details_from_git(self):
		if self.use_ssh:
			_first_part, _second_part = self.name.split(":")
			self.remote_server = _first_part.split("@")[-1]
			self.org, _repo = _second_part.rsplit("/", 1)
		else:
			self.remote_server, self.org, _repo = self.name.rsplit("/", 2)

		self.tag = self.branch
		self.repo = _repo.split(".")[0]

	@property
	def url(self):
		if self.from_apps:
			return os.path.abspath(os.path.join("apps", self.name))

		if self.on_disk:
			return self.mount_path

		if self.is_url:
			return self.name

		if self.use_ssh:
			return self.get_ssh_url()

		return self.get_http_url()

	def get_http_url(self):
		return f"https://{self.remote_server}/{self.org}/{self.repo}.git"

	def get_ssh_url(self):
		return f"git@{self.remote_server}:{self.org}/{self.repo}.git"


@functools.lru_cache(maxsize=None)
class App(AppMeta):
	def __init__(
		self, name: str, branch: str = None, pine: "Pine" = None, *args, **kwargs
	):
		self.pine = pine
		super().__init__(name, branch, *args, **kwargs)

	@step(title="Fetching App {repo}", success="App {repo} Fetched")
	def get(self):
		branch = f"--branch {self.tag}" if self.tag else ""
		shallow = "--depth 1" if self.pine.shallow_clone else ""

		fetch_txt = f"Getting {self.repo}"
		click.secho(fetch_txt, fg="yellow")
		logger.log(fetch_txt)

		self.pine.run(
			f"git clone {self.url} {branch} {shallow} --origin upstream",
			cwd=os.path.join(self.pine.name, "apps"),
		)

	@step(title="Archiving App {repo}", success="App {repo} Archived")
	def remove(self):
		active_app_path = os.path.join("apps", self.repo)
		archived_path = os.path.join("archived", "apps")
		archived_name = get_available_folder_name(
			f"{self.repo}-{date.today()}", archived_path
		)
		archived_app_path = os.path.join(archived_path, archived_name)
		log(f"App moved from {active_app_path} to {archived_app_path}")
		shutil.move(active_app_path, archived_app_path)

	@step(title="Installing App {repo}", success="App {repo} Installed")
	def install(self, skip_assets=False, verbose=False, restart_pine=True):
		import pine.cli
		from pine.utils.app import get_app_name

		verbose = pine.cli.verbose or verbose
		app_name = get_app_name(self.pine.name, self.repo)

		# TODO: this should go inside install_app only tho - issue: default/resolved branch
		setup_app_dependencies(
			repo_name=self.repo,
			pine_path=self.pine.name,
			branch=self.tag,
			verbose=verbose,
			skip_assets=skip_assets,
		)

		install_app(
			app=app_name,
			pine_path=self.pine.name,
			verbose=verbose,
			skip_assets=skip_assets,
			restart_pine=restart_pine
		)

	@step(title="Uninstalling App {repo}", success="App {repo} Uninstalled")
	def uninstall(self):
		self.pine.run(f"{self.pine.python} -m pip uninstall -y {self.repo}")


def add_to_appstxt(app, pine_path="."):
	from pine.pine import Pine

	apps = Pine(pine_path).apps

	if app not in apps:
		apps.append(app)
		return write_appstxt(apps, pine_path=pine_path)


def remove_from_appstxt(app, pine_path="."):
	from pine.pine import Pine

	apps = Pine(pine_path).apps

	if app in apps:
		apps.remove(app)
		return write_appstxt(apps, pine_path=pine_path)


def write_appstxt(apps, pine_path="."):
	with open(os.path.join(pine_path, "sites", "apps.txt"), "w") as f:
		return f.write("\n".join(apps))


def get_excluded_apps(pine_path="."):
	try:
		with open(os.path.join(pine_path, "sites", "excluded_apps.txt")) as f:
			return f.read().strip().split("\n")
	except IOError:
		return []


def add_to_excluded_apps_txt(app, pine_path="."):
	if app == "melon":
		raise ValueError("Melon app cannot be excludeed from update")
	if app not in os.listdir("apps"):
		raise ValueError(f"The app {app} does not exist")
	apps = get_excluded_apps(pine_path=pine_path)
	if app not in apps:
		apps.append(app)
		return write_excluded_apps_txt(apps, pine_path=pine_path)


def write_excluded_apps_txt(apps, pine_path="."):
	with open(os.path.join(pine_path, "sites", "excluded_apps.txt"), "w") as f:
		return f.write("\n".join(apps))


def remove_from_excluded_apps_txt(app, pine_path="."):
	apps = get_excluded_apps(pine_path=pine_path)
	if app in apps:
		apps.remove(app)
		return write_excluded_apps_txt(apps, pine_path=pine_path)


def setup_app_dependencies(
	repo_name, pine_path=".", branch=None, skip_assets=False, verbose=False
):
	# branch kwarg is somewhat of a hack here; since we're assuming the same branches for all apps
	# for eg: if you're installing monak@develop, you'll want melon@develop and healthcare@develop too
	import glob
	import pine.cli
	from pine.pine import Pine

	verbose = pine.cli.verbose or verbose
	apps_path = os.path.join(os.path.abspath(pine_path), "apps")
	files = glob.glob(os.path.join(apps_path, repo_name, "**", "hooks.py"))

	if files:
		with open(files[0]) as f:
			lines = [x for x in f.read().split("\n") if x.strip().startswith("required_apps")]
		if lines:
			required_apps = eval(lines[0].strip("required_apps").strip().lstrip("=").strip())
			# TODO: when the time comes, add version check here
			for app in required_apps:
				if app not in Pine(pine_path).apps:
					get_app(
						app,
						pine_path=pine_path,
						branch=branch,
						skip_assets=skip_assets,
						verbose=verbose,
					)


def get_app(
	git_url,
	branch=None,
	pine_path=".",
	skip_assets=False,
	verbose=False,
	overwrite=False,
	init_pine=False,
):
	"""pine get-app clones a Melon App from remote (GitHub or any other git server),
	and installs it on the current pine. This also resolves dependencies based on the
	apps' required_apps defined in the hooks.py file.

	If the pine_path is not a pine directory, a new pine is created named using the
	git_url parameter.
	"""
	from pine.pine import Pine
	import pine as _pine
	import pine.cli as pine_cli

	pine = Pine(pine_path)
	app = App(git_url, branch=branch, pine=pine)
	git_url = app.url
	repo_name = app.repo
	branch = app.tag
	pine_setup = False
	restart_pine = not init_pine

	if not is_pine_directory(pine_path):
		if not init_pine:
			raise NotInPineDirectoryError(
				f"{os.path.realpath(pine_path)} is not a valid pine directory. "
				"Run with --init-pine if you'd like to create a Pine too."
			)

		from pine.utils.system import init

		pine_path = get_available_folder_name(f"{app.repo}-pine", pine_path)
		init(path=pine_path, melon_branch=branch)
		os.chdir(pine_path)
		pine_setup = True

	if pine_setup and pine_cli.from_command_line and pine_cli.dynamic_feed:
		_pine.LOG_BUFFER.append({
			"message": f"Fetching App {repo_name}",
			"prefix": click.style('⏼', fg='bright_yellow'),
			"is_parent": True,
			"color": None,
		})

	cloned_path = os.path.join(pine_path, "apps", repo_name)
	dir_already_exists = os.path.isdir(cloned_path)
	to_clone = not dir_already_exists

	# application directory already exists
	# prompt user to overwrite it
	if dir_already_exists and (
		overwrite
		or click.confirm(
			f"A directory for the application '{repo_name}' already exists. "
			"Do you want to continue and overwrite it?"
		)
	):
		shutil.rmtree(cloned_path)
		to_clone = True

	if to_clone:
		app.get()

	if (
		to_clone
		or overwrite
		or click.confirm("Do you want to reinstall the existing application?")
	):
		app.install(verbose=verbose, skip_assets=skip_assets, restart_pine=restart_pine)


def new_app(app, no_git=None, pine_path="."):
	if pine.MELON_VERSION in (0, None):
		raise NotInPineDirectoryError(
			f"{os.path.realpath(pine_path)} is not a valid pine directory."
		)

	# For backwards compatibility
	app = app.lower().replace(" ", "_").replace("-", "_")
	apps = os.path.abspath(os.path.join(pine_path, "apps"))
	args = ["make-app", apps, app]
	if no_git:
		if pine.MELON_VERSION < 7:
			click.secho(
				"Melon v7 or greater is needed for '--no-git' flag",
				fg="red"
			)
			return
		args.append(no_git)

	logger.log(f"creating new app {app}")
	run_melon_cmd(*args, pine_path=pine_path)
	install_app(app, pine_path=pine_path)


def install_app(
	app,
	pine_path=".",
	verbose=False,
	no_cache=False,
	restart_pine=True,
	skip_assets=False,
):
	import pine.cli as pine_cli
	from pine.pine import Pine

	install_text = f"Installing {app}"
	click.secho(install_text, fg="yellow")
	logger.log(install_text)

	pine = Pine(pine_path)
	conf = pine.conf

	verbose = pine_cli.verbose or verbose
	quiet_flag = "" if verbose else "--quiet"
	cache_flag = "--no-cache-dir" if no_cache else ""

	app_path = os.path.realpath(os.path.join(pine_path, "apps", app))

	pine.run(f"{pine.python} -m pip install {quiet_flag} --upgrade -e {app_path} {cache_flag}")

	if conf.get("developer_mode"):
		install_python_dev_dependencies(apps=app, pine_path=pine_path, verbose=verbose)

	if os.path.exists(os.path.join(app_path, "package.json")):
		pine.run("yarn install", cwd=app_path)

	pine.apps.sync()

	if not skip_assets:
		build_assets(pine_path=pine_path, app=app)

	if restart_pine:
		pine.reload()


def pull_apps(apps=None, pine_path=".", reset=False):
	"""Check all apps if there no local changes, pull"""
	from pine.pine import Pine
	from pine.utils.app import get_current_branch, get_remote

	pine = Pine(pine_path)
	rebase = "--rebase" if pine.conf.get("rebase_on_pull") else ""
	apps = apps or pine.apps
	excluded_apps = pine.excluded_apps

	# check for local changes
	if not reset:
		for app in apps:
			if app in excluded_apps:
				print(f"Skipping reset for app {app}")
				continue
			app_dir = get_repo_dir(app, pine_path=pine_path)
			if os.path.exists(os.path.join(app_dir, ".git")):
				out = subprocess.check_output("git status", shell=True, cwd=app_dir)
				out = out.decode("utf-8")
				if not re.search(r"nothing to commit, working (directory|tree) clean", out):
					print(
						f"""

Cannot proceed with update: You have local changes in app "{app}" that are not committed.

Here are your choices:

1. Merge the {app} app manually with "git pull" / "git pull --rebase" and fix conflicts.
1. Temporarily remove your changes with "git stash" or discard them completely
	with "pine update --reset" or for individual repositries "git reset --hard"
	"""
					)
					sys.exit(1)

	for app in apps:
		if app in excluded_apps:
			print(f"Skipping pull for app {app}")
			continue
		app_dir = get_repo_dir(app, pine_path=pine_path)
		if os.path.exists(os.path.join(app_dir, ".git")):
			remote = get_remote(app)
			if not remote:
				# remote is False, i.e. remote doesn't exist, add the app to excluded_apps.txt
				add_to_excluded_apps_txt(app, pine_path=pine_path)
				print(
					f"Skipping pull for app {app}, since remote doesn't exist, and"
					" adding it to excluded apps"
				)
				continue

			if not pine.conf.get("shallow_clone") or not reset:
				is_shallow = os.path.exists(os.path.join(app_dir, ".git", "shallow"))
				if is_shallow:
					s = " to safely pull remote changes." if not reset else ""
					print(f"Unshallowing {app}{s}")
					pine.run(f"git fetch {remote} --unshallow", cwd=app_dir)

			branch = get_current_branch(app, pine_path=pine_path)
			logger.log(f"pulling {app}")
			if reset:
				reset_cmd = f"git reset --hard {remote}/{branch}"
				if pine.conf.get("shallow_clone"):
					pine.run(f"git fetch --depth=1 --no-tags {remote} {branch}", cwd=app_dir)
					pine.run(reset_cmd, cwd=app_dir)
					pine.run("git reflog expire --all", cwd=app_dir)
					pine.run("git gc --prune=all", cwd=app_dir)
				else:
					pine.run("git fetch --all", cwd=app_dir)
					pine.run(reset_cmd, cwd=app_dir)
			else:
				pine.run(f"git pull {rebase} {remote} {branch}", cwd=app_dir)
			pine.run('find . -name "*.pyc" -delete', cwd=app_dir)


def use_rq(pine_path):
	pine_path = os.path.abspath(pine_path)
	celery_app = os.path.join(pine_path, "apps", "melon", "melon", "celery_app.py")
	return not os.path.exists(celery_app)


def get_repo_dir(app, pine_path="."):
	return os.path.join(pine_path, "apps", app)


def install_apps_from_path(path, pine_path="."):
	apps = get_apps_json(path)
	for app in apps:
		get_app(
			app["url"], branch=app.get("branch"), pine_path=pine_path, skip_assets=True,
		)


def get_apps_json(path):
	import requests

	if path.startswith("http"):
		r = requests.get(path)
		return r.json()

	with open(path) as f:
		return json.load(f)
