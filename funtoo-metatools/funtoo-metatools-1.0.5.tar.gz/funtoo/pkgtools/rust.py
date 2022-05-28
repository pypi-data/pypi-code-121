import glob
import os
import subprocess
import toml

import dyne.org.funtoo.metatools.pkgtools as pkgtools


async def get_crates_artifacts(lock_path):
	"""
	This method will extract package data from ``Cargo.lock`` and generate Artifacts for all packages it finds.
	"""
	with open(lock_path, "r") as f:
		crates_raw = f.read()
	crates_dict = toml.loads(crates_raw)
	crates = ""
	crates_artifacts = []
	for package in crates_dict["package"]:
		if "source" not in package:
			continue
		crates = crates + package["name"] + "-" + package["version"] + "\n"
		crates_url = "https://crates.io/api/v1/crates/" + package["name"] + "/" + package["version"] + "/download"
		crates_file = package["name"] + "-" + package["version"] + ".crate"
		crates_artifacts.append(pkgtools.ebuild.Artifact(url=crates_url, final_name=crates_file))
	return dict(crates=crates, crates_artifacts=crates_artifacts)


async def generate_crates_from_artifact(src_artifact, src_dir_glob="*"):
	"""
	This method, when passed an Artifact, will fetch the artifact, extract it, look in the directory
	``src_dir_glob`` (a glob specifying the name of the source directory within the extracted files
	which contains ``Cargo.lock`` -- you can also specify sub-directories as part of this glob), and
	will then parse ``Cargo.lock`` for package names, and then generate a list of artifacts for each
	crate discovered. This list of new artifacts will be returned as a list. In the case there is no
	``Cargo.lock`` present in the artifact, ``cargo update`` will be run to generate one.
	"""
	await src_artifact.fetch()
	src_artifact.extract()
	src_dir = glob.glob(os.path.join(src_artifact.extract_path, src_dir_glob))[0]
	cargo_lock_path = os.path.join(src_dir, "Cargo.lock")
	if not os.path.exists(cargo_lock_path):
		cargo_cmd = subprocess.Popen(["cargo", "update"], cwd=src_dir).wait()
	artifacts = await get_crates_artifacts(cargo_lock_path)
	src_artifact.cleanup()
	return artifacts
