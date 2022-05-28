import hashlib
import os
from collections import OrderedDict
from typing import Mapping, Optional

from bson import UuidRepresentation
from bson.codec_options import TypeRegistry
from bson.json_util import dumps, JSONOptions, loads

# Notes:
#
# So far, what I have for a FileStore works great, as long as the process/thread has exclusive access
# to the underlying data since there is no locking.
#
# To work around the locking issue, one possibility is to have every datastore fronted by a separate
# process or distinct, dedicated thread that implements a ZeroMQ protocol that others can connect to
# utilize the datastore. This would cause all requests to be processed linearly while still offering
# high performance and flexibility.
#
# Below:
# This is equivalent to CANONICAL_JSON_OPTIONS, but we use OrderedDicts for representing objects (good to
# ensure consistency when storing/retrieving dictionaries)

JSON_OPTIONS = JSONOptions(
			strict_number_long=True, datetime_representation=1, strict_uuid=True, json_mode=2,
			document_class=OrderedDict, tz_aware=False, uuid_representation=UuidRepresentation.UNSPECIFIED,
			unicode_decode_error_handler='strict', tzinfo=None,
			type_registry=TypeRegistry(type_codecs=[], fallback_encoder=None))


class NotFoundError(Exception):
	pass


def extract_data_by_keyspec(index_field, data):
	"""
	This method accepts a string like "foo.bar", and will traverse dict hierarchy ``metadata``
	to retrieve the specified element. Each '.' represents a depth in the dictionary hierarchy.
	"""
	index_split = index_field.split(".")
	cur_data = data
	for index_part in index_split:
		if index_part not in cur_data:
			raise KeyError(f"Attempting to retrieve field {index_field}, but does not exist ({index_part})")
		elif not isinstance(cur_data, Mapping):
			raise KeyError(f"Attempting to retrieve field {index_field}, but did not find it in supplied data.")
		cur_data = cur_data[index_part]
	return cur_data


def expand_keyspec(keyspec):
	"""
	This function takes a mongo-style query string like::

	  { "pkginfo.cat" : "sys-apps", "pkginfo.pkg" : "portage" }

	...and will convert it to the actual dictionary we want to match, which would be::

	  { "pkginfo" : {
	    "cat" : "sys-apps",
	    "pkg" : "portage"
	  } }

	the store.read() and store.delete() methods take a KeySpec like the first example.
	"""
	out = {}
	for keyspec_atom, val in keyspec.items():
		keyspec_atom_split = keyspec_atom.split(".")
		cur_out = out
		for depth_atom in keyspec_atom_split[:-1]:
			if depth_atom not in cur_out:
				cur_out[depth_atom] = {}
			cur_out = cur_out[depth_atom]
		cur_out[keyspec_atom_split[-1]] = val
	return out


class Key:

	"""
	This is an abstract base class for a "Key", which is a type of key that is
	used for indexing and retrieving items from a Store.
	"""
	pass


class HashKey(Key):

	"""
	A ``HashKey`` is used when you are already storing a hash in the data in the
	store. In this case, you pass a "key specification" to the constructor which
	is a "dotted path" notation to the path of this hash within your data. Something
	like "hashes.sha512".
	"""

	def __init__(self, key_spec: str):
		assert isinstance(key_spec, str)
		self.key_spec = key_spec

	def __repr__(self):
		return f"HashKey({self.key_spec}"

	def data_as_hash(self, data):
		return extract_data_by_keyspec(self.key_spec, data)

	def validate_specdict(self, spec_dict):
		if self.key_spec not in spec_dict:
			raise KeyError(f"Was expecting {self.key_spec} to be specified for query.")

	def validate_data(self, data):
		extract_data_by_keyspec(self.key_spec, data)

	def specdict_as_hash(self, spec_dict):
		self.validate_specdict(spec_dict)
		return spec_dict[self.key_spec]


class DerivedKey(Key):

	"""
	A ``DerivedKey`` is a key generated from the JSON of one or more fields in your data.
	Pass a list of these fields, in dotted "key specification" format, to the constructor.
	This key type will then generate normalised JSON of these elements, and use this to
	construct a predictable hash which is used for indexing.

	The ``optional_spec_list`` is a list of elements that, if they do not exist in the
	data, are safe to simply omit from the key spec. This is useful when adding new fields
	to the key specification in new versions of metatools.
	"""

	def __init__(self, key_spec_list, optional_spec_list=None):
		self.key_spec_list = key_spec_list
		self.optional_spec_list = optional_spec_list if optional_spec_list is not None else []

	def __repr__(self):
		return f"DerivedKeys({self.key_spec_list})"

	def data_as_hash(self, data):
		return hashlib.sha512(dumps(self.compound_value(data), json_options=JSON_OPTIONS, sort_keys=True).encode("utf-8")).hexdigest()

	def compound_value(self, data):
		value = OrderedDict()
		for key_spec in self.key_spec_list:
			if key_spec in self.optional_spec_list:
				try:
					index_data = extract_data_by_keyspec(key_spec, data)
				except KeyError:
					continue
			else:
				index_data = extract_data_by_keyspec(key_spec, data)
			value[key_spec] = index_data
		return value

	def validate_data(self, data):
		for key_spec in self.key_spec_list:
			if key_spec not in self.optional_spec_list:
				extract_data_by_keyspec(key_spec, data)

	def validate_specdict(self, spec_dict):
		expected_set = set(self.key_spec_list)
		provided_set = set(spec_dict.keys())
		unrecognized = provided_set - expected_set
		missing = (expected_set - provided_set) - set(self.optional_spec_list)
		if unrecognized:
			raise KeyError(f"Unrecognized key specifications in query: {unrecognized}")
		if missing:
			raise KeyError(f"Missing key specifications in query: {missing}")

	def specdict_as_hash(self, spec_dict):
		self.validate_specdict(spec_dict)
		return self.data_as_hash(expand_keyspec(spec_dict))


class BLOBReference:
	pass


class BLOBDiskReference(BLOBReference):
	def __init__(self, path):
		self.path = path


class StoreObject:

	def __init__(self, data, blob_path=None):
		self.data = data
		if blob_path:
			self.blob = BLOBDiskReference(path=blob_path)


class StorageBackend:

	"""
	This is an abstract class for a storage backend. This class hierarchy allows for
	the ``Store`` class to be re-targetable to different types of backends by choosing
	different implementations of this class.
	"""

	store = None

	def create(self, store):
		self.store = store

	def write(self, data, blob_path=None) -> Optional[StoreObject]:
		pass

	def read(self, spec_dict) -> Optional[StoreObject]:
		pass

	def delete(self, data) -> None:
		pass


class FileStorageBackend(StorageBackend):

	"""
	This is the primary storage backend used with the ``Store`` class, which is
	designed to store data directly on disk in a series of directories organized
	by a hash key.

	This storage backend has the ability to store 'data', which is structured
	data stored in JSON format (although thanks to BSON does a much better job
	with Python data formats like datetime, etc.), as well as the ability to
	store an associated 'blob' -- which can be arbitrary binary data such as
	a downloaded source tarball.
	"""
	root = None

	def __init__(self, db_base_path):
		self.db_base_path = db_base_path

	def create(self, store):
		self.store = store
		self.root = os.path.join(self.db_base_path, self.store.collection)
		if self.store.prefix is not None:
			self.root = os.path.join(self.root, self.store.prefix)
		os.makedirs(self.root, exist_ok=True)

	def encode_data(self, data) -> bytes:
		# We sort the keys so we always have a consistent representation of dictionary keys on disk.
		return dumps(data, json_options=JSON_OPTIONS, sort_keys=True).encode('utf-8')

	def decode_data(self, path) -> OrderedDict:
		with open(path, "rb") as f:
			in_string = f.read().decode("utf-8")
			return loads(in_string, json_options=JSON_OPTIONS)

	def write(self, data, blob_path=None) -> Optional[StoreObject]:
		sha = self.store.key_spec.data_as_hash(data)
		dir_index = f"{sha[0:2]}/{sha[2:4]}/{sha[4:6]}"
		out_path = f"{self.root}/{dir_index}/{sha}"
		os.makedirs(os.path.dirname(out_path), exist_ok=True)
		return self._write_phase2(out_path, data, blob_path)

	def _write_phase2(self, out_path, data, blob_path=None) -> Optional[StoreObject]:
		os.makedirs(os.path.dirname(out_path), exist_ok=True)
		with open(out_path, 'wb') as f:
			f.write(self.encode_data(data))
		if blob_path:
			blob_outpath = out_path + ".blob"
			if os.path.exists(blob_outpath):
				os.unlink(blob_outpath)
			# Downloading two different URLs which point to the exact same binary can result in races. This happens with
			# crates:
			#
			#     File "/home/drobbins/development/funtoo-metatools/metatools/store.py", line 236, in write
			#         return self._write_phase2(out_path, data, blob_path)
			#       File "/home/drobbins/development/funtoo-metatools/metatools/store.py", line 246, in _write_phase2
			#         os.link(blob_path, blob_outpath)
			#     FileExistsError: [Errno 17] File exists:
			#
			# The try/except clause below prevents this collision from causing problems.
			try:
				os.link(blob_path, blob_outpath)
			except FileExistsError:
				pass
		else:
			blob_outpath = None
		return StoreObject(data=data, blob_path=blob_outpath)

	def read(self, spec_dict) -> Optional[StoreObject]:
		sha = self.store.key_spec.specdict_as_hash(spec_dict)
		dir_index = f"{sha[0:2]}/{sha[2:4]}/{sha[4:6]}"
		in_path = f"{self.root}/{dir_index}/{sha}"
		if not os.path.exists(in_path):
			return None
		blob_path = in_path + ".blob"
		return StoreObject(data=self.decode_data(in_path), blob_path=blob_path if os.path.exists(blob_path) else None)

	def delete(self, spec_dict) -> None:
		sha = self.store.key_spec.specdict_as_hash(spec_dict)
		dir_index = f"{sha[0:2]}/{sha[2:4]}/{sha[4:6]}"
		in_path = f"{self.root}/{dir_index}/{sha}"
		if os.path.exists(in_path):
			os.unlink(in_path)
		blob_path = in_path + ".blob"
		if os.path.exists(blob_path):
			os.unlink(blob_path)


class Store:

	"""
	This is the ``Store`` class which is the class intended to be instantiated and used by
	other code. You will typically also pass it a ``FileStorageBackend()`` for it to
	initialize, which will actually store your data on disk. However, in the future it
	will be possible to easily add other types of backends if desired.
	"""

	backend: StorageBackend = None
	collection = None
	prefix = None
	key_spec = None
	required_spec = None

	def __init__(self, collection=None, prefix=None, key_spec=None, required_spec=None, backend=None):
		if collection is not None:
			self.collection = collection
		if prefix is not None:
			self.prefix = prefix
		if key_spec is not None:
			self.key_spec = key_spec
		if required_spec is not None:
			self.required_spec = required_spec
		if backend is not None:
			self.backend = backend
		self.backend.create(self)

	def write(self, data, blob_path=None) -> Optional[StoreObject]:
		if self.required_spec:
			self.required_spec.validate_data(data)
		return self.backend.write(data, blob_path=blob_path)

	def read(self, spec_dict: dict) -> Optional[StoreObject]:
		return self.backend.read(spec_dict)

	def delete(self, key_spec: dict) -> None:
		return self.backend.delete(key_spec)
