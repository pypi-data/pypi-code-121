#!/usr/bin/python3

# Context -> (can we even tweak this? ideally we don't have it reading from args or env directly, so we can!)
#   Configuration ->
#     Entry Point (can tweak configuration) ->
#       Model (gets config) ->
#         Initialization of subsystem (in process of entry point)
#                                |
#                                \ subpop should make entry points accessible by other pieces of code, not just
#                                  from the command-line.
#                                  It can do this by having an explicit configuration pipeline rather than leaving
#                                  things to the setuptools entrypoint to do everything. So we want to model this in
#                                  code.
#                                  We should be able to mark subsystems as needing initialization or not.
#
#
# import dyne.org.funtoo.org.metatools.merge as merge
#
# config = {
#	"env" : None,
#	"user": None,
#	"config":
#       "main" : "~/.foo/bar"
#}

# one-stage launch:
# await hub.launch(merge, payload={"regen"}, config=None)
#
# Even without payloads, you need to launch, because that's how you provide config. The only way you wouldn't need to
# launch is if you don't have any config.
#
# two-stage launch:
#
# model = await hub.pre_launch(merge, payload={"regen"}, config)
# (tweak/interact with model)
# await merge.launch(model=model)
#
# orbit.model <-- the subsystem-specific hub? mapped into namespace?
# orbit.foo
import os

from subpop.config import SubPopModel


# Components: fastpull: spider
#             regen. full tree regen?
#             autogen: a doit run
#             deepdive: deepdive querying


class MinimalConfig(SubPopModel):
	"""
	This class contains configuration settings common to all the metatools plugins and tools.
	"""

	db_name = "metatools2"

	def __init__(self):
		super().__init__()

	@property
	def work_path(self):
		home = self.home()
		if home:
			return os.path.join(home, "repo_tmp")
		else:
			return "/var/tmp/repo_tmp"

	@property
	def source_trees(self):
		return os.path.join(self.work_path, "source-trees")

	@property
	def store_path(self):
		return os.path.join(self.work_path, "stores")

	@property
	def fetch_download_path(self):
		return os.path.join(self.work_path, "fetch")

	@property
	def temp_path(self):
		"""
		merge-kits may run multiple 'doit's in parallel. In this case, we probably want to segregate their temp
		paths. We can do this by having a special option passed to doit which can in turn tweak the Configuration
		object to create unique sub-paths here.
		This is TODO item!
		"""
		home = self.home()
		if home:
			return os.path.join(home, "repo_tmp/tmp")
		else:
			return "/var/tmp/repo_tmp/tmp"

	@property
	def fastpull_path(self):
		"""
		In theory, multiple fastpull hooks could try to link the same file into the same fastpull location at
		the same time resulting in a code failure.

		Possibly, we could have a 'staging' fastpull for each 'doit' call, and the master merge-kits process
		could look in this area and move files into its main fastpull db from its main process rather than
		relying on each 'doit' process to take care of it.

		Maybe this only happens when 'doit' is run as part of merge-kits. When run separately, 'doit' would
		populate the main fastpull db itself.

		In any case, some resiliency in the code for multiple creation of the same symlink (and thus symlink
		creation failure) would be a good idea.

		"""

		return os.path.join(self.work_path, "fastpull")




