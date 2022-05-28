#!/usr/bin/env python3
import logging
from collections import defaultdict

LICENSE_CLASSIFIER_MAP = {
	"License :: OSI Approved :: Apache Software License": "Apache-2.0",
	"License :: OSI Approved :: BSD License": "BSD",
	"License :: OSI Approved :: MIT License": "MIT",
}


def pypi_license_to_gentoo(classifiers):
	"""
	This function will use our (currently very minimal) mapping of pypi license classifiers to Gentoo
	license names. Note that "||" syntax is not used since the classifiers do not support this.

	Empty string is returned if no license info is found, or if no licenses match.
	"""
	global LICENSE_CLASSIFIER_MAP
	license_set = set()
	for classifier in classifiers:
		if not classifier.startswith("License :: "):
			continue
		if classifier in LICENSE_CLASSIFIER_MAP:
			license_set.add(LICENSE_CLASSIFIER_MAP[classifier])
	return " ".join(sorted(list(license_set)))


def pypi_metadata_init(local_pkginfo, json_dict):
	"""
	This function initializes metadata for the package based on pypi (and also sets defaults for things like
	inherit.)
	"""
	if "inherit" not in local_pkginfo:
		local_pkginfo["inherit"] = []
	if "distutils-r1" not in local_pkginfo["inherit"]:
		local_pkginfo["inherit"].append("distutils-r1")
	if "desc" not in local_pkginfo:
		local_pkginfo["desc"] = json_dict["info"]["summary"]
	if "homepage" not in local_pkginfo:
		local_pkginfo["homepage"] = json_dict["info"]["home_page"]+" "+json_dict["info"]["project_url"]
	if "license" not in local_pkginfo:
		local_pkginfo["license"] = pypi_license_to_gentoo(json_dict["info"]["classifiers"])


def sdist_artifact_url(releases, version):
	# Sometimes a version does not have a source tarball. This function lets us know if our version is legit.
	# Returns artifact_url for version, or None if no sdist release was available.
	for artifact in releases[version]:
		if artifact["packagetype"] == "sdist":
			return artifact["url"]
	return None


def pypi_normalize_name(pkginfo):
	if "pypi_name" not in pkginfo:
		pkginfo["pypi_name"] = pkginfo["name"]
	return pkginfo["pypi_name"]


def pypi_normalize_version(pkginfo):
	version_parts = pkginfo["version"].split(".")
	if version_parts[-1].startswith("post"):
		ebuild_version = ".".join(version_parts[:-1]) + "_p" + version_parts[-1][4:]
	else:
		ebuild_version = pkginfo["version"]
	pkginfo["pypi_version"] = pkginfo["version"]
	pkginfo["version"] = ebuild_version


def pypi_get_artifact_url(pkginfo, json_dict, strict=True):
	"""
	A more robust version of ``sdist_artifact_url``.

	Look in JSON data ``json_dict`` retrieved from pypi for the proper sdist artifact for the package specified in
	pkginfo. If ``strict`` is True, will insist on the ``version`` defined in ``pkginfo``, otherwise, will be flexible
	and fall back to most recent sdist.
	"""
	artifact_url = sdist_artifact_url(json_dict["releases"], pkginfo["version"])
	if artifact_url is None:
		if not strict:
			# dang, the latest official release doesn't have a source tarball. Let's scan for the most recent release with a source tarball:
			for version in reversed(json_dict["releases"].keys()):
				artifact_url = sdist_artifact_url(json_dict["releases"], version)
				if artifact_url is not None:
					pkginfo["version"] = version
					break
		else:
			raise AssertionError(f"Could not find a source distribution for {pkginfo['name']} version {pkginfo['version']}")
	else:
		artifact_url = sdist_artifact_url(json_dict["releases"], pkginfo["version"])
	return artifact_url


def expand_pydep(pkginfo, pyatom):
	"""
	Takes something from our pydeps YAML that might be "foo", or "sys-apps/foo", or "foo >= 1.2" and convert to
	the proper Gentoo atom format.
	"""
	# TODO: support ranges?
	# TODO: pass a ctx variable here so we can have useful error messages about what pkg is triggering the error.
	psp = pyatom.split()
	if not len(psp):
		raise ValueError(f"{pkginfo['cat']}/{pkginfo['name']} appears to have invalid pydeps. Make sure each pydep is specified as a YAML list item starting with '-'.")
	if psp[0] == "not!":
		block = "!"
		psp = psp[1:]
	else:
		block = ""
	if len(psp) == 3 and psp[1] in [">", ">=", "<", "<="]:
		if "/" in psp[0]:
			# already has a category
			return f"{block}{psp[1]}{psp[0]}-{psp[2]}[${{PYTHON_USEDEP}}]"
		else:
			# inject dev-python
			return f"{block}{psp[1]}dev-python/{psp[0]}-{psp[2]}[${{PYTHON_USEDEP}}]"
	elif len(psp) == 1:
		if "/" in pyatom:
			return f"{block}{psp[0]}[${{PYTHON_USEDEP}}]"
		else:
			# inject dev-python
			return f"{block}dev-python/{psp[0]}[${{PYTHON_USEDEP}}]"
	else:
		raise ValueError(f"{pkginfo['cat']}/{pkginfo['name']} appears to have an invalid pydep '{pyatom}'.")


def create_ebuild_cond_dep(pkginfo, pydeplabel, atoms):
	"""
	This function takes a specifier like "py:all" and a list of simplified pythony package atoms and creates a
	conditional dependency for inclusion in an ebuild. It returns a list of lines (without newline termination,
	each string in the list implies a separate line.)
	"""
	out_atoms = []
	pyspec = None
	usespec = None
	if pydeplabel.dep_type == "py":
		pyspec = pydeplabel.gen_cond_dep()
	elif pydeplabel.dep_type == "use":
		usespec = list(pydeplabel.specifiers)[0]

	for atom in atoms:
		out_atoms.append(expand_pydep(pkginfo, atom))

	if usespec:
		out = [f"{usespec}? ( {' '.join(out_atoms)} )"]
	elif not len(pyspec):
		# no condition -- these deps are for all python versions, so not a conditional dep:
		out = out_atoms
	else:
		# stuff everything into a python_gen_cond_dep:
		out = [r"$(python_gen_cond_dep '"] + out_atoms + [r"' " + " ".join(pyspec), ")"]
	return out


class InvalidPyDepLabel(Exception):

	def __init__(self, label, errmsg=None):
		self.label = label
		self.errmsg = errmsg

	def __str__(self):
		out = f"{self.label.pydep_label}"
		if self.errmsg:
			out += " " + self.errmsg
		return out


class ParsedPyDepLabel:

	def __init__(self, pydep_label):
		self.pydep_label = pydep_label
		self.dep_type = None
		self.mods = set()
		self._ver_set = set()
		self.has_2x_version = False
		self.has_3x_version = False
		self.parse()

	def parse(self):
		parts = self.pydep_label.split(":")
		if not len(parts):
			raise InvalidPyDepLabel(self)
		if parts[0] not in ["use", "py"]:
			raise InvalidPyDepLabel(self)
		self.dep_type = parts[0]
		if len(parts) == 3:
			self.mods = set(parts[-1].split(","))
		if self.dep_type == "py":
			self._ver_set = set(parts[1].split(","))
		else:
			self._ver_set = {parts[1]}
		self._validate_ver_set()

	def _validate_ver_set(self):
		if self.dep_type != "py":
			return True
		if self._ver_set & {"3", "all"}:
			self.has_3x_version = True
		if self._ver_set & {"2", "all"}:
			self.has_2x_version = True
		remaining = self._ver_set - {"3", "2", "all", "pypy", "pypy3"}
		for ver_spec in list(remaining):
			if ver_spec.startswith("2."):
				self.has_2x_version = True
			elif ver_spec.startswith("3."):
				self.has_3x_version = True
			if ver_spec == "pypy3":
				self.has_3x_version = True
			remaining.remove(ver_spec)
		if len(remaining):
			raise InvalidPyDepLabel(self)

	@property
	def specifiers(self):
		return sorted(list(self._ver_set))

	def has_specifier(self, ver):
		return ver in self._ver_set

	@property
	def build_dep(self):
		return "build" in self.mods

	@property
	def post_dep(self):
		return "post" in self.mods

	@property
	def runtime_dep(self):
		return "runtime" in self.mods or len(self.mods) == 0

	@property
	def tool_dep(self):
		return "tool" in self.mods

	@property
	def py2_enabled(self):
		"""
		Tell us if this dependency should be enabled on compat ebuilds.
		"""
		if self.dep_type == "py" and not self.has_2x_version:
			return False
		return True

	@property
	def py3_enabled(self):
		"""
		Tell us if this dependency should be enabled on py3-only ebuilds.
		"""
		if self.dep_type == "py" and not self.has_3x_version:
			return False
		return True

	def gen_cond_dep(self):
		"""
		This method takes a parsed pydep label and converts it to a list of arguments that should
		be passed to python_gen_cond_dep (eclass function.) Protect ourselves from the weird syntax in this eclass.

		 py:all -> [] (meaning "no restriction", i.e. apply to all versions)
		 py:2,3.7,3.8 -> [ "-2", "python3_7", "python3_8"]

		"""
		assert self.dep_type == "py"
		if "all" in self._ver_set:
			return []
		out = []
		for pg_item in self._ver_set:
			if pg_item in ["2", "3"]:
				out += [f"-{pg_item}"]  # -2, etc.
			elif "." in pg_item:
				# 2.7 -> python2_7, etc.
				out += [f"python{pg_item.replace('.', '_')}"]
			else:
				# pass thru pypy, pypy3, etc.
				out.append(pg_item)
		return out


def expand_pydeps(pkginfo, compat_mode=False, compat_ebuild=False):
	expanded_pydeps = defaultdict(list)
	if "pydeps" in pkginfo:
		pytype = type(pkginfo["pydeps"])
		if pytype == list:
			for dep in pkginfo["pydeps"]:
				# super-simple pydeps are just considered runtime deps
				expanded_pydeps["rdepend"].append(expand_pydep(pkginfo, dep))
		elif pytype == dict:
			for label_str, deps in pkginfo["pydeps"].items():
				label = ParsedPyDepLabel(label_str)
				if compat_mode:
					if compat_ebuild and not label.py2_enabled:
						continue
					elif not compat_ebuild and not label.py3_enabled:
						continue
				cond_dep = create_ebuild_cond_dep(pkginfo, label, deps)
				if label.build_dep:
					expanded_pydeps["depend"] += cond_dep
				if label.runtime_dep:
					expanded_pydeps["rdepend"] += cond_dep
				if label.post_dep:
					expanded_pydeps["pdepend"] += cond_dep
				if label.tool_dep:
					expanded_pydeps["bdepend"] += cond_dep
	for dep_type in ["depend", "rdepend", "pdepend", "bdepend"]:
		deps = expanded_pydeps[dep_type]
		if not deps:
			continue
		if dep_type not in pkginfo:
			pkginfo[dep_type] = "\n".join(deps)
		else:
			pkginfo[dep_type] += "\n" + "\n".join(deps)
	return None
