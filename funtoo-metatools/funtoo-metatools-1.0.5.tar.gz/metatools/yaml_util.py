#!/usr/bin/env python3

import io
import yaml


class YAMLReader:

	def start(self):
		"""
		Override this method in subclasses to easily add any initialization.
		"""
		pass

	def __init__(self, stream):
		self.yaml = yaml.safe_load(stream)
		self.start()

	def get_elem(self, el_path):
		"""
		This method returns an element at a specified path. If it exists, the subtree will be returned.
		Otherwise, None will be returned.
		"""
		el_split = el_path.split('/')
		yaml_root = self.yaml
		for item in el_split:
			if item not in yaml_root:
				return
			yaml_root = yaml_root[item]
		return yaml_root

	def iter_groups(self, el_path):
		"""
		Similar to self.iter_list() but works on groups not list items.
		"""
		el_split = el_path.split('/')
		yaml_root = self.yaml
		for item in el_split:
			if item not in yaml_root:
				return
			yaml_root = yaml_root[item]
		for key, val in yaml_root.items():
			yield key, val

	def iter_list(self, el_path):
		"""
		This is designed to be an iterator to go over list items at a specific depth. Use an xpath-like path, such as
		"foo/bar", for the following YAML, to sequentially iterate over 'oni' and 'jones'::

		  foo:
		    bar:
		      - oni:
		        blarg: blarg
		      - jones

		If the path doesn't exist, then no elements will be yielded.
		"""
		el_split = el_path.split('/')
		yaml_root = self.yaml
		for item in el_split:
			if item not in yaml_root:
				return
			yaml_root = yaml_root[item]
		for list_item in yaml_root:
			yield list_item


if __name__ == "__main__":
	yaml_test = io.StringIO("""
foo:
  bar:
    - oni
    - jones:
        blarg: blarg
""")
	reader = YAMLReader(yaml_test)
	for item in reader.iter_list("foo/bar"):
		print(item)

