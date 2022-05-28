#!/usr/bin/python3


import os

import pymongo
from pymongo import MongoClient


def fetch_cache():
	mc = MongoClient()
	fc = mc.db.fetch_cache
	fc.create_index([("method_name", pymongo.ASCENDING), ("url", pymongo.ASCENDING)])
	fc.create_index("last_failure_on", partialFilterExpression={"last_failure_on": {"$exists": True}})
	return fc

def deepdive():
	mc = MongoClient()
	dd = mc.db.deepdive
	dd.create_index("atom")
	dd.create_index([("kit", pymongo.ASCENDING), ("category", pymongo.ASCENDING), ("package", pymongo.ASCENDING)])
	dd.create_index("catpkg")
	dd.create_index("relations")
	dd.create_index("md5")
	dd.create_index("files.name", partialFilterExpression={"files": {"$exists": True}})
	return dd


class DistfileIntegrity:

	def __init__(self):
		mc = MongoClient()
		di = self.c = mc.db.distfile_integrity
		di.create_index([("category", pymongo.ASCENDING), ("package", pymongo.ASCENDING), ("distfile", pymongo.ASCENDING)])

	def get(self, catpkg=None, key=None, distfile=None):
		if catpkg:
			return self.c.find_one({"catpkg": catpkg, "distfile": distfile})
		elif key:
			return self.c.find_one({"catpkg": key, "distfile": distfile})
		else:
			raise AttributeError("Must specify catpkg or key for distfile integrity lookup.")

	def store(self, catpkg_or_key, final_name, final_data, **kwargs):
		"""
		Store something in the distfile integrity database. This method is not thread-safe so you should call it from the
		main thread of 'doit' and not a sub-thread.
		"""
		out = {"catpkg": catpkg_or_key, "distfile": final_name, "final_data": final_data}
		for extra in "release", "kit", "branch":
			if extra in kwargs:
				out[extra] = kwargs[extra]

		self.c.insert_one(out)


def iter_thirdpartymirror(mirr_dict, mirror):
	if mirror not in mirr_dict:
		return None
	for mirr_url in mirr_dict[mirror]:
		yield mirr_url


def expand_thirdpartymirror(mirr_dict, url):

	non_mirr_part = url[9:]
	mirr_split = non_mirr_part.split("/")
	mirror = mirr_split[0]
	rest_of_url = "/".join(mirr_split[1:])
	if mirror not in mirr_dict:
		print("Mirror", mirror, "not found")
		return None
	for mirr_url in mirr_dict[mirror]:
		if mirror == "gentoo" and mirr_url.startswith("https://fastpull-us"):
			continue
		final_url = mirr_url.rstrip("/") + "/" + rest_of_url
		return final_url


class FastPull:

	def expand_uris(self, third_party_mirrors, src_uri_list):
		real_uri = []
		for src_uri in src_uri_list:
			if src_uri.startswith("mirror://"):
				real_uri.append(expand_thirdpartymirror(third_party_mirrors, src_uri))
			else:
				slash_split = src_uri.split("/")
				if len(slash_split) == 0:
					continue
				elif slash_split[0] not in ["http:", "https:", "ftp:"]:
					continue
				real_uri.append(src_uri)
		return real_uri

	def get_disk_path(self, sh):
		return os.path.join(self.fastpull_path, sh[:2], sh[2:4], sh[4:6], sh)

	def parse_mcafee_logs(self, logf, path_prefix="/opt"):
		"""
		This method takes a McAfee Virus Scanner log file as an argument, and will scan the log for filenames that showed
		up in it. This is useful for when things in the fastpull mirror are showing up in a McAfee scan. The function will
		then extract the sha512's and return these as a list.

		The McAfee logs use "-" at the end of line to indicate the line is continued on the next line. This function has
		to potentially re-assemble split sha512 digests, as well as detect mutiple files listed on a single line.
		"""
		out_digests = []
		with open(logf, "r") as f:
			lines = f.readlines()
			new_lines = []
			pos = 0
			while pos < len(lines):
				cur_line = lines[pos].strip()
				pos += 1
				if path_prefix not in cur_line:
					continue

				while cur_line.endswith("-"):
					cur_line = cur_line[:-1] + lines[pos + 1]
					pos += 1

				new_lines.append(cur_line)

			for line in new_lines:
				ls = line.split()
				for part in ls:
					if part.startswith("/opt"):
						part_strip = part.rstrip(",")
						out_digests.append(part_strip.split("/")[-1])

		return out_digests
