#!/usr/bin/env python3

import asyncio
import inspect
import logging
import os
import subprocess
from asyncio import FIRST_EXCEPTION, Task
from collections import defaultdict
from concurrent.futures.thread import ThreadPoolExecutor

import dyne.org.funtoo.metatools.pkgtools as pkgtools
from subpop.util import load_plugin
from yaml import safe_load

"""
The `PENDING_QUE` will be built up to contain a full list of all the catpkgs we want to autogen in the full run
of 'doit'. We queue up everything first so that we have the ability to add QA checks, such as for catpkgs that
are defined multiple times and other errors that we should catch before processing begins. The work is organized
by the generator (pop plugin) that will be used to generate a list of catpkgs. Before we start, we have
everything organized so that we only need to call `execute_generator` once for each generator. It will start
work for all catpkgs in that generator, and wait for completion of this work before returning.
"""

PENDING_QUE = []
AUTOGEN_FAILURES = []


SUB_FP_MAP_LOCK = asyncio.Lock()
SUB_FP_MAP = {}

"""
While it is possible for a `generate()` function to call the `generate()` method on a `BreezyBuild` directly,
in nearly all cases the `BreezyBuild`'s `push` method is called to queue it for processing. When `push` is
called, we want to start the `generate` method as an asyncio `Task` and then keep track of it so we can wait for
all of these `Tasks` to complete.

When these tasks are running, they are using a specific generator (pop plugin) and we want to be able to wait
for these tasks to complete after we have processed all the work for the generator. This is for two reasons --
so we can enforce a limit for the number of generators running at once, and so we do not exit prematurely while
generators have still not completed their work.

`BREEZYBUILD_TASKS` is configured to hold these tasks. They are organized by the 'sub-index', which is a string
name we use to reference the generator internally. That way we can segregate our tasks by generator, which is
important so each generator can wait for only its own tasks to complete.
"""

BREEZYBUILDS_PENDING = defaultdict(list)
BREEZYBUILD_TASKS_ACTIVE = defaultdict(list)
BREEZYBUILD_SUB_INDEX_HANDOFF = {}


def generate_manifests():
	"""
	Once auto-generation is complete, this function will write all stored Manifest data to disk. We do this after
	autogen completes so we can ensure that all necessary ebuilds have been created and we can ensure that these are
	written once for each catpkg, rather than written as each individual ebuild is autogenned (which would create a
	race condition writing to each Manifest file.)
	"""
	for manifest_file, manifest_lines in pkgtools.model.manifest_lines.items():
		manifest_lines = sorted(list(manifest_lines))
		with open(manifest_file, "w") as myf:
			pos = 0
			while pos < len(manifest_lines):
				myf.write(manifest_lines[pos])
				pos += 1
		logging.debug(f"Manifest {manifest_file} generated.")


def queue_all_indy_autogens():
	"""
	This will find all independent autogens and queue them up in the pending queue.
	"""
	s, o = subprocess.getstatusoutput("find %s -iname autogen.py 2>&1" % pkgtools.model.locator.start_path)
	files = o.split("\n")
	for file in files:
		file = file.strip()
		if not len(file):
			continue

		subpath = os.path.dirname(file)
		if subpath.endswith("metatools"):
			continue

		pkg_name = file.split("/")[-2]
		pkg_cat = file.split("/")[-3]

		PENDING_QUE.append(
			{
				"gen_path": subpath,
				"generator_sub_path": subpath,
				"template_path": os.path.join(subpath, "templates"),
				"pkginfo_list": [{"name": pkg_name, "cat": pkg_cat}],
			}
		)
		logging.debug(f"Added to queue of pending autogens: {PENDING_QUE[-1]}")


async def gather_pending_tasks(task_list):
	"""
	This function collects completed asyncio coroutines, catches any exceptions recorded during their execution.
	"""
	results = []
	cur_tasks = task_list
	if not len(cur_tasks):
		return [], []
	while True:
		done_list, cur_tasks = await asyncio.wait(cur_tasks, return_when=FIRST_EXCEPTION)
		# TODO: Due to the way we are setting a _handle for each Task, which is handling any exceptions, I don't think
		#       we still need to handle any exceptions here.
		for done_item in done_list:
			try:
				result = done_item.result()
				results.append(result)
			except Exception as e:
				pkgtools.model.log.error("Unexpected Exception!")
				raise e
		if not len(cur_tasks):
			break
	return results


def init_pkginfo_for_package(generator_sub, sub_path, defaults=None, base_pkginfo=None, template_path=None, gen_path=None):
	"""
	This function generates the final pkginfo that is passed to the generate() function in the generator sub
	for each catpkg being generated.

	we create the pkginfo data that gets passed to generate. You can see that it can come from multiple places:

	1. A generator sub can define a `GLOBAL_DEFAULTS` dictionary that contains global settings. These are
	   set first.

	2. Then, any defaults that are provided to us, which have come from the `defaults:` section of the
	   autogen.yaml are supplied. (`defaults`, below.)

	3. Next, `cat` and `name` settings calculated based on the path of the `autogen.py`, or the settings that
	   come from the package-specific part of the `autogen.yaml` are added on top. (`base_pkginfo`, below.),
	   plus any non-'version' sections from the package-specific section.
	"""
	glob_defs = getattr(generator_sub, "GLOBAL_DEFAULTS", {})
	pkginfo = glob_defs.copy()
	if defaults is not None:
		pkginfo.update(defaults)
	pkginfo.update(base_pkginfo)
	if template_path:
		pkginfo["template_path"] = template_path
	pkginfo["sub_path"] = sub_path
	# Now that we have wrapped the generate method, we need to start it as an asyncio task and then we will wait
	# for all our generate() calls to complete, outside this for loop.

	# This is the path where the autogen lives. Either the autogen.py or the autogen.yaml:
	common_prefix = os.path.commonprefix([pkgtools.model.locator.root, gen_path])
	path_from_root = gen_path[len(common_prefix):].lstrip("/")
	pkginfo["gen_path"] = f"${{REPODIR}}/{path_from_root}"
	return pkginfo


def _handle_task_result(task: Task):
	try:
		success = task.result()
		if not success:
			fail_info = getattr(task, 'info', None)
			if fail_info:
				AUTOGEN_FAILURES.append(fail_info)
			else:
				AUTOGEN_FAILURES.append("Unknown Autogen!")
	except asyncio.CancelledError:
		pass
	except Exception as e:
		fail_info = getattr(task, 'info', None)
		if fail_info:
			AUTOGEN_FAILURES.append(fail_info)
		else:
			AUTOGEN_FAILURES.append("Unknown Autogen (2)!")


def _artifact_handle_task_result(task: Task):
	try:
		task.result()
	except asyncio.CancelledError:
		pass
	except Exception as e:
		pkgtools.model.log.error(e, exc_info=True)
	# TODO: record these failures in a global place if this is still a valid exception-catching path.


async def execute_generator(
	generator_sub_path=None,
	generator_sub_name="autogen",
	template_path=None,
	defaults=None,
	pkginfo_list=None,
	gen_path=None,
	autogen_id=None
):
	"""
	This function will return an async function that requires no arguments, that is ready to run in its own
	thread using run_async_adapter. This function will execute the full auto-generation for a particular
	generator/autogen.py and will wait until all of its asyncio tasks have completed before returning. This
	neatly allows an autogeneration for a sub/generator/autogen.py to be contained in its own thread, improving
	performance and allowing the use of thread-local storage to keep track of things specific to this autogen
	run.
	"""
	if not generator_sub_path:
		raise TypeError("generator_sub_path not set to a path.")
	sub_path = f"{generator_sub_path}/{generator_sub_name}.py"
	generator_sub = load_plugin(sub_path, generator_sub_name)
	# Do hub injection:
	generator_sub.hub = hub
	generator_sub.sub_path = sub_path
	generator_sub.FOO = "bar"

	async def generator_thread_task(pkginfo_list):

		hub.THREAD_CTX.running_autogens = []
		hub.THREAD_CTX.running_breezybuilds = []
		hub.THREAD_CTX.genned_breezybuilds = set()

		# Do our own internal processing to get pkginfo_list ready for generate().

		new_pkginfo_list = []
		for base_pkginfo in pkginfo_list:
			new_pkginfo_list.append(
				init_pkginfo_for_package(
					generator_sub,
					sub_path,
					defaults=defaults, base_pkginfo=base_pkginfo, template_path=template_path, gen_path=gen_path
				)
			)
		pkginfo_list = new_pkginfo_list

		# The generator now has the ability to make arbitrary modifications to our pkginfo_list (YAML).
		# Packages can be dropped or added, or their pkginfo arbitrarily modified using Python code.
		# See if ``preprocess_packages()`` exists in the generator -- and if it does, run it.

		preprocess_func = getattr(generator_sub, "preprocess_packages", None)
		if preprocess_func is not None:
			pkginfo_list = [i async for i in preprocess_func(hub, pkginfo_list)]

		for pkginfo in pkginfo_list:
			try:
				if "version" in pkginfo and pkginfo["version"] != "latest":
					logging.info(f"Autogen: {pkginfo['cat']}/{pkginfo['name']}-{pkginfo['version']}")
				else:
					logging.info(f"Autogen: {pkginfo['cat']}/{pkginfo['name']} (latest)")
			except KeyError as ke:
				raise pkgtools.ebuild.BreezyError(
					f"{generator_sub_name} encountered a key error: missing value. pkginfo is {pkginfo}. Missing in pkginfo: {ke}"
				)

			logging.debug(f"Using the following pkginfo for auto-generation: {pkginfo}")

			# Any .push() calls on BreezyBuilds will cause new tasks for those to be appended to
			# hub.THREAD_CTX.running_breezybuilds. This will happen during this task execution:

			async def gen_wrapper(pkginfo, generator_sub):

				# AutoHub is an evolution of the Hub. The hub is becoming less and less important
				# in subpop but has a purpose as a convenient thing in metatools autogens. We want
				# people to use the hub to directly instantiate objects easily, and also access all
				# of pkgtools. We want ad-hoc autogens to be instantiated as hub.Artifact() not
				# hub.pkgtools.ebuild.Artifact().

				# WIP: work to remove direct access to pkgtools.ebuild and reroute to this hub instead.
				# I got distracted on supporting subpop stuff for this.

				#class FinderWrapper:
				#
				#	def __init__(self, orig, ebuild):
				#		self.orig = orig
				#		self.ebuild = ebuild
				#
				#	def __getattr__(self, item):
				#		if item == "ebuild":
				#			return self.ebuild
				#		else:
				#			return getattr(self.orig, item)

				class AutoHub:

					autogen_id = None
					sub_path = generator_sub_path
					THREAD_CTX = hub.THREAD_CTX
					get_page = pkgtools.fetch.get_page
					temp_path = pkgtools.model.temp_path

					def __init__(self, autogen_id, pkgtools):
						self.autogen_id = autogen_id
						#self.pkgtools = FinderWrapper(pkgtools, self)
						self.pkgtools = pkgtools

					def Artifact(self, **kwargs):
						return pkgtools.ebuild.Artifact(key=self.autogen_id, **kwargs)

					def BreezyBuild(self, **kwargs):
						return pkgtools.ebuild.BreezyBuild(**kwargs)

					def BreezyError(self, **kwargs):
						return pkgtools.ebuild.BreezyError(**kwargs)

					def __getattr__(self, item):
						if item == "pkgtools":
							return self.pkgtools

				if "version" in pkginfo and pkginfo["version"] != "latest":
					autogen_info = f"{pkginfo['cat']}/{pkginfo['name']}-{pkginfo['version']}"
				else:
					autogen_info = f"{pkginfo['cat']}/{pkginfo['name']} (latest)"

				generate = getattr(generator_sub, "generate", None)
				if generate is None:
					return autogen_info, AttributeError(f"generate() not found in {generator_sub}")
				try:
					try:
						await generate(AutoHub(autogen_id, pkgtools), **pkginfo)
					except TypeError as te:
						if not inspect.iscoroutinefunction(generate):
							pkgtools.model.log.error(f"generate() in {generator_sub} must be async")
							return False
						else:
							pkgtools.model.log.error(te, exc_info=True)
							raise te
				except Exception as e:
					pkgtools.model.log.error(e, exc_info=True)
					return False
				return True

			task = Task(gen_wrapper(pkginfo, generator_sub))

			# task.info is used for error messages. Try to add catpkg info in it if it exists:
			task.info = sub_path
			if "cat" in pkginfo and "name" in pkginfo:
				task.info += f" ({pkginfo['cat']}/{pkginfo['name']})"

			task.add_done_callback(_handle_task_result)
			hub.THREAD_CTX.running_autogens.append(task)

		await gather_pending_tasks(hub.THREAD_CTX.running_autogens)
		await gather_pending_tasks(hub.THREAD_CTX.running_breezybuilds)

	return generator_thread_task, pkginfo_list


def parse_yaml_rule(package_section=None):

	pkginfo_list = []
	defaults = {}
	if isinstance(package_section, str):

		# A simple '- pkgname' one-line format:
		#
		# - foobar
		#
		pkginfo_list.append({"name": package_section})

	elif isinstance(package_section, dict):

		# A more complex format, where the package has sub-settings.
		#
		# - foobar:
		#     val1: blah
		#     val2: bleh
		#
		# { 'foobar' : { 'val1' : 'blah', 'val2' : 'bleh' } }

		# Remove extra singleton outer dictionary (see format above)

		package_name = list(package_section.keys())[0]
		pkg_section = list(package_section.values())[0]
		pkg_section["name"] = package_name

		# This is even a more complex format, where we have sub-sections based on versions of the package,
		# each with their own settings. And we can also have other values which set defaults for this package:
		#
		# - foobar:
		#     another_setting:
		#       blah: morf
		#     versions:
		#       1.2.4:
		#         val1: blah
		#       latest:
		#         val1: bleeeeh

		if isinstance(pkg_section, dict) and "versions" in pkg_section:
			versions_section = pkg_section["versions"]

			# Grab any other values as defaults:
			v_defaults = pkg_section.copy()
			del v_defaults["versions"]

			for version, v_pkg_section in versions_section.items():
				v_pkginfo = {"name": package_name}
				v_pkginfo.update(v_defaults)
				v_pkginfo.update(v_pkg_section)
				v_pkginfo["version"] = version
				pkginfo_list.append(v_pkginfo)
		else:
			pkginfo_list.append(pkg_section)

	return defaults, pkginfo_list


def queue_all_yaml_autogens():

	"""
	This function finds all autogen.yaml files in the repository and adds work to the `PENDING_QUE` (via calls
	to `parse_yaml_rule`.) This queues up all generators to execute.
	"""

	s, o = subprocess.getstatusoutput("find %s -iname autogen.yaml 2>&1" % pkgtools.model.locator.start_path)
	files = o.split("\n")

	for file in files:
		file = file.strip()
		if not len(file):
			continue
		yaml_base_path = os.path.dirname(file)
		# This will be [ "category", "pkgname" ] or [ "category" ] if it's nestled inside a category dir:
		yaml_base_path_split = yaml_base_path[len(pkgtools.model.locator.root) + 1:].split("/")
		if len(yaml_base_path_split):
			cat = yaml_base_path_split[0]
		else:
			cat = None

		with open(file, "r") as myf:
			for rule_name, rule in safe_load(myf.read()).items():

				if "defaults" in rule:
					defaults = rule["defaults"].copy()
				else:
					defaults = {}
				if "cat" not in defaults and cat is not None:
					defaults["cat"] = cat
				if "generator" in rule:
					sub_path = os.path.join(yaml_base_path, "generators")
					sub_name = rule["generator"]
					if os.path.exists(os.path.join(sub_path, rule["generator"] + ".py")):
						# We found a generator in a "generators" directory next to the autogen.yaml that contains the
						# generator.
						logging.debug(f"Found generator {sub_name} in local tree.")
					elif pkgtools.model.current_repo != pkgtools.model.kit_fixups_repo and \
						os.path.exists(os.path.join(pkgtools.model.current_repo.root, "generators", rule["generator"] + ".py")):
						# if we are running doit inside "foo-sources", look in the local repo /generators too.
						sub_path = os.path.join(pkgtools.model.current_repo.root, "generators")
					elif os.path.exists(os.path.join(pkgtools.model.kit_fixups_repo.root, "generators", rule["generator"] + ".py")):
						# fall back to kit-fixups/generators.
						sub_path = os.path.join(pkgtools.model.kit_fixups_repo.root, "generators")
					else:
						raise pkgtools.ebuild.BreezyError("Required generator \'{rule['generator']}\' not found.")
				else:
					# Fallback: Use an ad-hoc 'generator.py' generator in the same dir as autogen.yaml:
					sub_name = "generator"
					sub_path = yaml_base_path

				pkginfo_list = []
				for package in rule["packages"]:
					package_defaults, parsed_pkg = parse_yaml_rule(package_section=package)
					pkginfo_list += parsed_pkg
					defaults.update(package_defaults)

				PENDING_QUE.append(
					{
						"gen_path": yaml_base_path,
						"generator_sub_name": sub_name,
						"generator_sub_path": sub_path,
						"template_path": os.path.join(yaml_base_path, "templates"),
						"defaults": defaults,
						"pkginfo_list": pkginfo_list,
					}
				)
				logging.debug(f"Added to queue of pending autogens: {PENDING_QUE[-1]}")


async def execute_all_queued_generators():
	futures = []
	loop = asyncio.get_running_loop()
	with ThreadPoolExecutor(max_workers=16) as executor:
		while len(PENDING_QUE):
			task_args = PENDING_QUE.pop(0)

			# The "autogen_id" entry here is going to be used like an ID for distfile integrity Artifacts that aren't
			# attached to a specific BreezyBuild.

			base = os.path.commonprefix([task_args["gen_path"], pkgtools.model.locator.root])
			task_args["autogen_id"] = f"{pkgtools.model.kit_spy}:{task_args['gen_path'][len(base)+1:]}"
			async_func, pkginfo_list = await execute_generator(**task_args)
			future = loop.run_in_executor(executor, hub.run_async_adapter, async_func, pkginfo_list)
			futures.append(future)

		await gather_pending_tasks(futures)


async def start():
	# This is a hack to iterate through all plugins to ensure they are all loaded prior to starting threads, so we
	# don't experience race conditions loading modules, as this clobbers sys.modules in a non-threadsafe way currently.
	for plugin in pkgtools:
		pass
	queue_all_indy_autogens()
	queue_all_yaml_autogens()
	await execute_all_queued_generators()
	generate_manifests()
	# TODO: return false on error
	if len(AUTOGEN_FAILURES):
		if len(AUTOGEN_FAILURES) == 1:
			pkgtools.model.log.error(f"An error was encountered when processing {AUTOGEN_FAILURES[0]}")
		else:
			pkgtools.model.log.error(f"Errors were encountered when processing the following autogens:")
			for fail in AUTOGEN_FAILURES:
				pkgtools.model.log.error(f" * {fail}")
		return False
	else:
		return True


# vim: ts=4 sw=4 noet
