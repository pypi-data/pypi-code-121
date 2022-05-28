#!/usr/bin/env python3

import logging
from datetime import datetime

from metatools.blos import BaseLayerObjectStore
from metatools.fastpull.spider import FetchRequest, Download
from metatools.store import Store, FileStorageBackend, DerivedKey, StoreObject

log = logging.getLogger('metatools.autogen')


class IntegrityScope:

	def __init__(self, parent, scope, validate_hashes=None):
		if validate_hashes is None:
			validate_hashes = {"sha512"}
		self.validate_hashes = validate_hashes
		self.parent = parent
		self.scope = scope
		self.store = Store(
			collection="integrity",
			prefix=self.scope,
			backend=FileStorageBackend(db_base_path=self.parent.db_base_path),
			key_spec=DerivedKey(["url"])
		)

	async def get_file_by_url(self, request: FetchRequest) -> StoreObject:
		"""

		This method will attempt to return a StoreObject reference to binary data which is associated with
		a URL, referenced by ``request.url``, in this ``IntegrityScope``. Typically, this means that a
		tarball is being requested, and we may have this tarball already available locally, or we may
		need to use the ``Spider`` to download it. This is the method used to retrieve ``Artifact``s
		from the interwebs.

		If the object associated with the URL is available locally, a ``BLOSObject`` will be returned
		that references this object.

		In the case that the URL has not yet been retrieved and, it will be downloaded, and inserted into
		the BLOS, and a reference to this inserted file will be returned.

		If the file is currently in the process of being downloaded, but this download has not completed
		yet, this call will block until the download has completed, and then a reference to the resultant
		BLOSObject will be returned.

		The specific flow that will be followed is:

		We'll first look at our IntegrityScope and see if we have an existing reference ('ref') to this file,
		by looking it up by the ``request.url``. We may have a record for it in our IntegrityScope, in which case we can
		try to retrieve it from the BLOS, using the ``sha512`` hash as a 'link' to the file in the BLOS. If we have
		a ref, but the BLOS object is missing for some reason, we will raise an exception as this can indicate
		a problem with our BLOS and we should not try to fix this automatically.

		If we have no local copy in the BLOS, we will definitely have to start a fresh download. We will leverage
		the data in the FetchRequest and use the Spider to launch a streaming HTTP download. This will also transparently
		handle the situation where we are *currently downloading* this file, for another asyncio task, and will
		internally wait for this download to finish rather than launching a new download.

		If our request actually initiated a fresh download, then when the download completes, the
		``self.parent.fetch_completion_callback`` we specified will cause some actions to happen. The downloaded
		file will be injected into the BLOS.

		Whether we initiated the download or not, we will get back the result of this pipeline and get the
		BLOSObject for the inserted object returned to us. We will pass this object back to the caller.

		If there is some kind of FetchError that could not be managed, it will be raised by the Spider, so that
		the root cause of the fetch error can be propagated to the caller.
		"""

		existing_ref: StoreObject = self.store.read({"url": request.url})
		if existing_ref is not None:
			obj = self.parent.blos.read({"hashes.sha512": existing_ref.data['sha512']})
			if obj is not None:
				log.debug(f"IntegrityScope:{self.scope}._get_file_by_url_new: existing object found for ref {request.url}")
				return obj
		new_ref = await self.parent.spider.download(request, completion_pipeline=[self.parent.fetch_completion_callback])
		assert isinstance(new_ref, StoreObject)
		self.store.write({"url": request.url, "sha512": new_ref.data["hashes"]["sha512"], "updated_on": datetime.utcnow()})
		return new_ref


class IntegrityDatabase:

	def __init__(self, db_base_path, blos: BaseLayerObjectStore = None, spider=None, hashes: set = None):
		"""
		``blos`` is an instance of a Base Layer Object Store (used to store distfiles, indexed by their hashes,
		and also takes care of all integrity checking tasks for us.

		``spider`` is an instance of a WebSpider, which handles all downloading tasks for us.

		``hashes`` is a set of cryptographic hashes

		The fastpull database uses sha512 as a 'linking mechanism' to the Base Layer Object Store (BLOS). So only
		one hash needs to be recorded, since this is not an exhaustive integrity check (that is performed by the
		BLOS itself upon retrieval). This is stored in the 'sha512' key, which is not placed inside 'hashes' like
		it is in the BLOS. But we do not create an index for it, since we don't encourage retrieval of objects from
		fastpull by their hash. They should be retrieved by target URL (and scope). So we always want to retrieve
		the ref by the URL, then from the returned record, use the sha512 to see if the BLOS entry exists.
		"""
		assert hashes
		self.db_base_path = db_base_path
		self.hashes = hashes
		self.blos: BaseLayerObjectStore = blos
		self.spider = spider
		self.scopes = {}

	def get_scope(self, scope_id):
		"""
		This method returns an 'IntegrityScope', which is basically like a session for doit (autogen) to
		associate URLs with entries in the BLOS, or Base Layer Object Store.
		"""
		if scope_id not in self.scopes:
			self.scopes[scope_id] = IntegrityScope(self, scope_id)
		log.debug(f"FastPull Integrity Scope: {scope_id}")
		return self.scopes[scope_id]

	def fetch_completion_callback(self, download: Download) -> StoreObject:
		"""
		This method is intended to be called *once* when an actual in-progress download of a tarball (by
		the Spider) has completed. It performs several important finalization actions upon successful
		download:

		1. The downloaded file will be stored in the BLOS, and the resultant BLOSObject will be assigned to
		``response.blos_object``.

		2. The Spider will be told to clean up the temporary file, as it will not be accessed directly by
		   anyone -- only the permanent file inserted into the BLOS will be handed back (via
		   ``response.blos_object``.

		We pass this to any Download() object we instantiate so that it has proper post-actions defined
		for it.
		"""

		store_obj: StoreObject = self.blos.insert_download(download)
		self.spider.cleanup(download)
		return store_obj
