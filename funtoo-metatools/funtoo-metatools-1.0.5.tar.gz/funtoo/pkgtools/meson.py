import shutil
from enum import Enum
import glob
import json
import os.path
import subprocess


class MesonError(Exception):
	def __init__(self, msg):
		self.msg = msg


class MesonBuildOptionType(Enum):
	"""
	Enum of possible Meson build option types.
	"""
	STRING = "string"
	BOOLEAN = "boolean"
	COMBO = "combo"
	INTEGER = "integer"
	ARRAY = "array"


class MesonBuildOption:
	"""
	This class defines the structure of a Meson build option.
	"""

	def __init__(self, **kwargs):
		self.name: str = kwargs["name"]
		self.description: str = kwargs["description"]
		self.type: MesonBuildOptionType = MesonBuildOptionType(kwargs["type"])
		self.value = kwargs["value"]
		self.section: str = kwargs["section"]
		self.machine: str = kwargs["machine"]
		self.choices: list = kwargs.get("choices")


def init_build_info(src_dir):
	"""
	Initialize Meson build info in the given source directory.

	:param src_dir: path to source directory
	:type src_dir: str
	:rtype: None
	"""
	builddir = os.path.join(src_dir, "builddir")
	if os.path.exists(builddir):
		shutil.rmtree(builddir)
	return_code = subprocess.Popen(
		["meson", "builddir"],
		cwd=src_dir,
		stdout=subprocess.DEVNULL,
		stderr=subprocess.STDOUT
	).wait()

	if return_code != 0:
		raise MesonError(f"Meson returned non-zero return code: {return_code}")


def get_build_info_dir(src_dir):
	"""
	Get path to Meson build info directory.

	:param src_dir: path to source directory
	:type src_dir: str
	:returns meson build info directory
	:rtype: str
	"""
	return os.path.join(src_dir, "builddir", "meson-info")


def get_build_options(src_dir):
	"""
	Get available build options of the Meson project in the given source directory.

	:param src_dir: path to source directory
	:type src_dir: str
	:returns meson build options
	:rtype: list[MesonBuildOption]
	"""
	init_build_info(src_dir)

	build_info_dir = get_build_info_dir(src_dir)
	build_options_path = os.path.join(build_info_dir, "intro-buildoptions.json")

	with open(build_options_path, "r") as build_options_file:
		return json.load(build_options_file, object_hook=lambda data: MesonBuildOption(**data))


async def get_build_options_from_artifact(src_artifact, src_dir_glob="*"):
	"""
	Get available build options of the Meson project in the given artifact.

	:param src_artifact: source artifact
	:type src_artifact: Artifact
	:param src_dir_glob: glob pattern to locate the source dir
	:type src_dir_glob: str
	:returns meson build options
	:rtype list[MesonBuildOption]
	"""
	await src_artifact.fetch()
	src_artifact.extract()

	src_dir = glob.glob(os.path.join(src_artifact.extract_path, src_dir_glob))[0]
	build_options = get_build_options(src_dir)

	src_artifact.cleanup()
	# It is good to return a sorted list so any programmatic use of this data in ebuilds will
	# produce the options in a deterministic order (avoiding randomized order):
	return list(sorted(build_options, key=lambda x: x.name))
