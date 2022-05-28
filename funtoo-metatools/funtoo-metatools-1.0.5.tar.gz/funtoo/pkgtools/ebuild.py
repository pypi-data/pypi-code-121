#!/usr/bin/env python3

import asyncio
import logging
import os
import threading
from asyncio import Task
from collections import OrderedDict
from subprocess import getstatusoutput
from typing import Optional

import jinja2

from metatools.store import StoreObject

log = logging.getLogger('metatools.autogen')

import dyne.org.funtoo.metatools.pkgtools as pkgtools

from metatools.fastpull.spider import FetchError, FetchRequest

# This is not currently used, as what the Spider downloads at any given moment is considered to
# be authoritative. This may be used for tools that repopulate the BLOS, but is not otherwise
# needed.
#
# class DigestFailure(Exception):
# 	def __init__(self, artifact=None, kind=None, expected=None, actual=None):
# 		self.artifact = artifact
# 		self.kind = kind
# 		self.expected = expected
# 		self.actual = actual
#
# 	@property
# 	def message(self):
# 		out = f"Digest Failure for {self.artifact.final_name}:\n"
# 		out += f"    Kind: {self.kind}\n"
# 		out += f"Expected: {self.expected}\n"
# 		out += f"  Actual: {self.actual}"
# 		return out
#


class BreezyError(Exception):
	def __init__(self, msg):
		self.msg = msg


class Fetchable:
	def __init__(self, url=None, **kwargs):
		self.url = url
		assert self.url is not None
		try:
			assert self.url.split(':')[0] in ['http', 'https', 'ftp']
		except (IndexError, AssertionError):
			raise ValueError(f"url= argument of Artifact is '{url}', which appears invalid.")


class Artifact(Fetchable):
	"""
	An artifact is a tarball or other archive that is used by a BreezyBuild, and ultimately referenced in an ebuild. It's also
	possible that an artifact could be fetched by an autogen directly, but not included in an ebuild.

	If an artifact is going to be incorporated into an ebuild, it's passed to the ``artifacts=[]`` keyword argument of the
	``BreezyBuild`` constructor. When it is passed in this way, we perform extra processing. We will store the resultant download
	in the "fastpull" database (an archive of fetched artifacts, indexed by their SHA512 hash), and we will also generate an
	entry in the "distfile integrity database" for each catpkg. This "distfile integrity database" is what links the BreezyBuild's
	catpkg, via the filename, to the entries in the fastpull database. So, for example:

	"sys-apps/foo-1.0.ebuild" references "foo-1.0.tar.gz".
	The distfile integrity database entry for "sys-apps/foo" has an entry for "foo-1.0.tar.gz" which points it to <SHA512>.
	The fastpull database stores an entry for <SHA512>.

	When an artifact is used in a stand-alone fashion

	"""
	def __init__(self, url=None, key=None, final_name=None, extra_http_headers=None, **kwargs):
		super().__init__(url=url, **kwargs)
		self.key = key
		self._final_name = final_name
		self.breezybuilds = []
		self.extra_http_headers = extra_http_headers
		self.blos_object: Optional[StoreObject] = None

	@property
	def final_data(self):
		if self.blos_object:
			return self.blos_object.data["hashes"]
		return None

	@property
	def catpkgs(self):
		outstr = ""
		for bzb in self.breezybuilds:
			outstr = f"{outstr} {bzb.catpkg}"
		return outstr.strip()

	@property
	def extract_path(self):
		return os.path.join(pkgtools.model.temp_path, "artifact_extract", self.final_name)

	@property
	def final_path(self):
		return self.blos_object.blob.path

	@property
	def final_name(self):
		if self._final_name is None:
			return self.url.split("/")[-1]
		else:
			return self._final_name

	async def fetch(self):
		await self.ensure_fetched()

	def is_fetched(self):
		return os.path.exists(self.final_path)

	@property
	def hashes(self):
		return self.blos_object.data["hashes"]

	@property
	def size(self):
		return self.blos_object.data["hashes"]["size"]

	def hash(self, h):
		return self.blos_object.data["hashes"][h]

	@property
	def src_uri(self):
		if self._final_name is None:
			return self.url
		else:
			return self.url + " -> " + self._final_name

	def extract(self):
		if not self.exists:
			self.fetch()
		ep = self.extract_path
		os.makedirs(ep, exist_ok=True)
		if self.final_name.endswith(".zip"):
			cmd = f"unzip {ep} -d {self.final_path}"
		else:
			cmd = f"tar -C {ep} -xf {self.final_path}"
		s, o = getstatusoutput(cmd)
		if s != 0:
			raise pkgtools.ebuild.BreezyError("Command failure: %s" % cmd)

	def cleanup(self):
		# TODO: check for path stuff like ../.. in final_name to avoid security issues.
		getstatusoutput("rm -rf " + os.path.join(pkgtools.model.temp_path, "artifact_extract", self.final_name))

	def exists(self):
		return self.is_fetched()

	async def ensure_fetched(self, throw=False) -> bool:
		"""
		This function ensures that the artifact is 'fetched' -- in other words, it exists locally. This means we can
		calculate its hashes or extract it.

		Returns a boolean with True indicating success and False failure in the default behavior with ``throw=False``,
		otherwise the original exception will be raised.
		"""

		if self.blos_object is not None:
			return True
		try:
			# TODO: add extra headers, retry,
			req = FetchRequest(self.url,
				extra_headers=self.extra_http_headers,
				# TODO: we currently don't support authenticating to retrieve an Artifact (just HTTP requests for API)
				username=None,
				password=None
			)
			log.debug(f'Artifact.ensure_fetched:{threading.get_ident()} now fetching {self.url} using FetchRequest {req}')
			# TODO: this used to be indexed by catpkg, and by final_name. So we are now indexing by source URL.
			# TODO: what exceptions are we interested in here?
			self.blos_object = await pkgtools.model.fastpull_session.get_file_by_url(req)
		except FetchError as fe:
			# We encountered some error retrieving the resource.
			if throw:
				raise fe
			log.error(f"Fetch error: {fe}")
			return False
		return True

	async def ensure_completed(self) -> bool:
		return await self.ensure_fetched()

	async def try_fetch(self):
		"""
		This is like ensure_fetched, but will return an exception if the download fails.
		"""
		await self.ensure_fetched(throw=True)


def aggregate(meta_list):
	out_list = []
	for item in meta_list:
		if isinstance(item, list):
			out_list += item
		else:
			out_list.append(item)
	return out_list


class BreezyBuild:

	cat = None
	name = None
	path = None
	template = None
	version = None
	_revision = None
	source_tree = None
	output_tree = None
	template_args = None

	@property
	def revision(self):
		if self._revision is None:
			self._revision = 0
		else:
			self.fixup_revision()
		return self._revision

	def __init__(
		self,
		artifacts=None,
		template: str = None,
		template_text: str = None,
		template_path: str = None,
		**kwargs,
	):
		self.source_tree = self.output_tree = pkgtools.model.locator.root
		self._pkgdir = None
		self.template_args = kwargs
		for kwarg in ["cat", "name", "version", "path"]:
			if kwarg in kwargs:
				setattr(self, kwarg, str(kwargs[kwarg]))
		if "revision" in kwargs:
			self._revision = kwargs["revision"]

		self.template = template
		self.template_text = template_text
		if template_path is None:
			if "path" in self.template_args:
				# If we have a pkginfo['path'], this gives us our current processing path.
				# Use this as a base for our default template path.
				self._template_path = os.path.join(self.template_args["path"] + "/templates")
			else:
				# This is a no-op, but wit this set to None, we will use the template_path()
				# property to get the value, which will be relative to the repo root and based
				# on the setting of name and category.
				self._template_path = None
		else:
			# A manual template path was specified.
			self._template_path = template_path
		if self.template_text is None and self.template is None:
			self.template = self.name + ".tmpl"
		if artifacts is None:
			self.artifacts = []
		else:
			self.artifacts = artifacts
		self.template_args["artifacts"] = artifacts

	def fixup_revision(self):
		"""
		Expand revision based on YAML structure which may have version-specific revision information, like this:

		revision:
		  2.0.0: 1

		We only want to apply this revision info if the version happens to match.
		"""
		if self._revision:
			if isinstance(self._revision, int):
				pass
			elif isinstance(self._revision, dict):
				if self.version in self._revision:
					self._revision = self._revision[self.version]
				else:
					self._revision = 0
			elif isinstance(self._revision, str):
				self._revision = int(self._revision)
			else:
				raise TypeError(f"Unrecognized type for revision= argument for {self.catpkg}: {repr(type(self._revision))}")
			pkgtools.model.log.debug(f"Fixup-revision: {self.catpkg}: {type(self._revision)} {self._revision}")

	def iter_artifacts(self):
		if type(self.artifacts) == list:
			for artifact in self.artifacts:
				yield artifact
		elif type(self.artifacts) in (dict, OrderedDict):
			for key, artifact in self.artifacts.items():
				yield artifact
		else:
			raise TypeError("Invalid type for artifacts passed to BreezyBuild -- should be list or dict.")

	async def setup(self):
		"""
		This method performs some special setup steps. We tend to treat Artifacts as stand-alone objects -- and they
		can be -- such as if you instantiate an Artifact in `generate()` and fetch it because you need to extract it
		and look inside it.

		But when associated with a BreezyBuild, as is commonly the case, this means that there is a relationship between
		the Artifact and the BreezyBuild.

		In this scenario, we know that the Artifact is associated with a catpkg, and will be written out to a Manifest.
		So this means we want to create some associations. We want to record that the Artifact is associated with the
		catpkg of this BreezyBuild. We use this for writing new entries to the Distfile Integrity database for
		to-be-fetched artifacts.
		"""

		fetch_tasks_dict = {}

		for artifact in self.iter_artifacts():
			if type(artifact) != Artifact:
				artifact = Artifact(**artifact)

			# This records that the artifact is used by this catpkg, because an Artifact can be shared among multiple
			# catpkgs. This is used for the integrity database writes:

			if self not in artifact.breezybuilds:
				artifact.breezybuilds.append(self)

			async def lil_coroutine(a):
				try:
					status = await a.ensure_completed()
					return a, status
				except Exception as e:
					pkgtools.model.log.error(e, exc_info=True)
					raise e

			fetch_task = asyncio.Task(lil_coroutine(artifact))
			fetch_task.add_done_callback(pkgtools.autogen._artifact_handle_task_result)
			fetch_tasks_dict[artifact] = fetch_task

		# Wait for any artifacts that are still fetching:
		results = await pkgtools.autogen.gather_pending_tasks(fetch_tasks_dict.values())
		completion_list = aggregate(results)
		for artifact, status in completion_list:
			if status is False:
				raise BreezyError(f"Artifact for url {artifact.url} referenced in {artifact.catpkgs} could not be fetched.")

	def push(self):
		#
		# https://stackoverflow.com/questions/1408171/thread-local-storage-in-python

		if self.output_ebuild_path in hub.THREAD_CTX.genned_breezybuilds:
			raise BreezyError(f"{self.output_ebuild_path} has already been generated -- you may have duplicate .push() calls or duplicate entries in your YAML.")
		else:
			hub.THREAD_CTX.genned_breezybuilds.add(self.output_ebuild_path)

		async def wrapper(self):
			try:
				await self.generate()
				return True
			except Exception as e:
				pkgtools.model.log.error(e, exc_info=True)
				return False

		# This will cause the BreezyBuild to start autogeneration immediately, appending the task to the thread-
		# local context so we can grab the result later. The return value will be the BreezyBuild object itself,
		# thanks to the wrapper.
		bzb_task = Task(wrapper(self))
		bzb_task.bzb = self
		bzb_task.info = self.catpkg_version_rev
		bzb_task.add_done_callback(pkgtools.autogen._handle_task_result)
		hub.THREAD_CTX.running_breezybuilds.append(bzb_task)

	@property
	def pkgdir(self):
		if self._pkgdir is None:
			self._pkgdir = os.path.join(self.source_tree, self.cat, self.name)
			os.makedirs(self._pkgdir, exist_ok=True)
		return self._pkgdir

	@property
	def output_pkgdir(self):
		if self._pkgdir is None:
			self._pkgdir = os.path.join(self.output_tree, self.cat, self.name)
			os.makedirs(self._pkgdir, exist_ok=True)
		return self._pkgdir

	@property
	def ebuild_name(self):
		if self.revision == 0:
			return "%s-%s.ebuild" % (self.name, self.version)
		else:
			return "%s-%s-r%s.ebuild" % (self.name, self.version, self.revision)

	@property
	def ebuild_path(self):
		return os.path.join(self.pkgdir, self.ebuild_name)

	@property
	def output_ebuild_path(self):
		return os.path.join(self.output_pkgdir, self.ebuild_name)

	@property
	def catpkg(self):
		return self.cat + "/" + self.name

	def __getitem__(self, key):
		return self.template_args[key]

	@property
	def catpkg_version_rev(self):
		if self.revision == 0:
			return self.cat + "/" + self.name + "-" + self.version
		else:
			return self.cat + "/" + self.name + "-" + self.version + "-r%s" % self.revision

	@property
	def template_path(self):
		if self._template_path:
			return self._template_path
		tpath = os.path.join(self.source_tree, self.cat, self.name, "templates")
		return tpath

	async def record_manifest_lines(self):
		"""
		This method records literal Manifest output lines which will get written out later, because we may
		not have *all* the Manifest lines we need to write out until autogen is fully complete.
		"""
		if not len(self.artifacts):
			return

		key = self.output_pkgdir + "/Manifest"

		for artifact in self.iter_artifacts():
			success = await artifact.ensure_completed()
			if not success:
				raise BreezyError(f"Something prevented us from storing Manifest data for {key}.")
			pkgtools.model.manifest_lines[key].add(
				"DIST %s %s BLAKE2B %s SHA512 %s\n"
				% (artifact.final_name, artifact.size, artifact.hash("blake2b"), artifact.hash("sha512"))
			)

	def create_ebuild(self):
		if not self.template_text:
			template_file = os.path.join(self.template_path, self.template)
			try:
				with open(template_file, "r") as tempf:
					try:
						template = jinja2.Template(tempf.read())
					except jinja2.exceptions.TemplateError as te:
						raise BreezyError(f"Template error in {template_file}: {repr(te)}")
					except Exception as te:
						raise BreezyError(f"Unknown error processing {template_file}: {repr(te)}")
			except FileNotFoundError as e:
				log.error(f"Could not find template: {template_file}")
				raise BreezyError(f"Template file not found: {template_file}")
		else:
			template = jinja2.Template(self.template_text)

		with open(self.output_ebuild_path, "wb") as myf:
			try:
				myf.write(template.render(**self.template_args).encode("utf-8"))
			except Exception as te:
				raise BreezyError(f"Error rendering template: {repr(te)}")
		log.info("Created: " + os.path.relpath(self.output_ebuild_path))

	async def generate(self):
		"""
		This is an async method that does the actual creation of the ebuilds from templates. It also handles
		initialization of Artifacts (indirectly) and could result in some HTTP fetching. If you call
		``myebuild.push()``, this is the task that gets pushed onto the task queue to run in parallel.
		If you don't call push() on your BreezyBuild, then you could choose to call the generate() method
		directly instead. In that case it will run right away.
		"""
		if self.cat is None:
			raise BreezyError("Please set 'cat' to the category name of this ebuild.")
		if self.name is None:
			raise BreezyError("Please set 'name' to the package name of this ebuild.")
		await self.setup()
		try:
			self.create_ebuild()
		except Exception as e:
			raise BreezyError(f"Error creating ebuild {self.catpkg}: {str(e)}")
		await self.record_manifest_lines()
		return self


# vim: ts=4 sw=4 noet
