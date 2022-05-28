#!/usr/bin/env python3
import asyncio
import re

from metatools.fastpull.spider import FetchError
from metatools.fetch_cache import CacheMiss

"""
This sub implements high-level fetching pkgtools.model.log.c. Not the lower-level HTTP stuff. Things involving
retrying, using our fetch cache, etc.
"""

import dyne.org.funtoo.metatools.pkgtools as pkgtools


async def fetch_harness(fetch_method, url, max_age=None, refresh_interval=None, **kwargs):

	"""
	This method is used to execute any fetch-related method, and will handle all the aspects of reading from and
	writing to the fetch cache, as needed, based on the current fetch policy. Arguments include ``fetch_method``
	which is the actual method used to fetch -- the function itself -- which should be a function or method that
	accepts a single non-keyword argument of the URL to fetch, and it should return the result of the fetch
	if successful, or raise FetchError on failure.

	The parameter ``url`` is of course the URL to fetch, and ``max_age`` is a timedelta which is passed to the
	``cache_read()`` method to specify a maximum age of the cached resource, used when using a CACHE_ONLY or
	LAZY fetch policy. ``refresh_interval`` is a timedelta which specifies the minimum interval before updating
	the cached resource and is only active if using BEST_EFFORT. This is useful for packages (like the infamous vim)
	that may get updated too frequently otherwise. Pass ``refresh_interval=timedelta(days=7)`` to only allow for
	updates to the cached metadata every 7 days. Default is None which means to refresh at will (no restrictions
	to frequency.)

	This function will raise FetchError if the result is unable to be retrieved, either from the cache or from
	the live network call -- except in the case of FetchPolicy.BEST_EFFORT, which will 'fall back' to the cache
	if the live fetch fails (and is thus more resilient).
	"""
	pkgtools.model.log.debug(f"refresh interval in fetch_harness: {refresh_interval}")
	attempts = 0
	fail_reason = None
	if refresh_interval is None:
		if pkgtools.model.fetch_cache_interval is not None:
			# pkgtools.model.fetch_cache_interval defaults to 15 minutes and will allow caching of stuff within that window
			# by default unless overridden by the doit --immediate option, or if there was an explicit refresh interval passed
			# to this function.
			refresh_interval = pkgtools.model.fetch_cache_interval

	# This may have "is_json", "encoding":
	key_dict = kwargs.copy()
	key_dict.update({
		"method_name": fetch_method.__name__,
		"url": url
	})
	
	while attempts < pkgtools.model.fetch_attempts:
		attempts += 1
		try:
			if refresh_interval is not None:
				# Let's see if we should use an 'older' resource that we don't want to refresh as often.

				# This call will return our cached resource if it's available and refresh_interval hasn't yet expired, i.e.
				# it is not yet 'stale'.
				try:
					result = await pkgtools.model.fetch_cache.read(
						key_dict=key_dict,
						refresh_interval=refresh_interval
					)
					if refresh_interval:
						pkgtools.model.log.info(f'Fetched {url} (cached, refresh_interval: {refresh_interval})')
					else:
						pkgtools.model.log.info(f'Fetched {url} (cached)')
					return result["body"]
				except CacheMiss:
					# We'll continue and attempt a live fetch of the resource...
					pass
			result = await fetch_method(url, **kwargs)
			await pkgtools.model.fetch_cache.write(key_dict=key_dict, body=result)
			return result
		except FetchError as e:
			if e.retry and attempts + 1 < pkgtools.model.fetch_attempts:
				pkgtools.model.log.error(f"Fetch method {fetch_method.__name__}: {e.msg}; retrying...")
				continue
			# if we got here, we are on our LAST retry attempt or retry is False:
			pkgtools.model.log.warning(f"Unable to retrieve {url}... trying to used cached version instead...")
			# TODO: these should be logged persistently so they can be investigated.
			try:
				# TODO: add kwargs here....
				got = await pkgtools.model.fetch_cache.read(key_dict=key_dict)
				return got["body"]
			except CacheMiss as ce:
				# raise original exception
				raise e
		except asyncio.CancelledError as e:
			raise FetchError(url, f"Fetch of {url} cancelled.")

	# If we've gotten here, we've performed all of our attempts to do live fetching.
	try:
		result = await pkgtools.model.fetch_cache.read(key_dict=key_dict, max_age=max_age)
		return result["body"]
	except CacheMiss:
		await pkgtools.model.fetch_cache.record_fetch_failure(key_dict=key_dict, fail_reason=fail_reason)
		raise FetchError(
			url,
			f"Unable to retrieve {url} using method {fetch_method.__name__} either live or from cache as fallback.",
		)


async def get_page(fetchable, max_age=None, refresh_interval=None, is_json=False):
	pkgtools.model.log.debug(f'get_page {fetchable}, max_age={max_age}, refresh_interval={refresh_interval}, is_json={is_json}')
	if isinstance(fetchable, pkgtools.ebuild.Artifact):
		fetchable = fetchable.url
	# Respect doit --immediate option:
	if pkgtools.model.fetch_cache_interval is not None:
		refresh_interval = pkgtools.model.fetch_cache_interval
	return await fetch_harness(pkgtools.http.get_page, fetchable, max_age=max_age, is_json=is_json, refresh_interval=refresh_interval)


async def get_response_headers(fetchable, max_age=None, refresh_interval=None):
	if isinstance(fetchable, pkgtools.ebuild.Artifact):
		fetchable = fetchable.url
	return await fetch_harness(
		pkgtools.http.get_response_headers, fetchable, max_age=max_age, refresh_interval=refresh_interval
	)


async def get_response_filename(fetchable, max_age=None, refresh_interval=None):
	"""
	This method gets the response's filename without fetching its body.
	This is achieved by looking at the `Content-Disposition` header.
	If the `Content-Disposition` header is not set or if it doesn't contain the filename,
	then it will return `None`.
	"""
	if isinstance(fetchable, pkgtools.ebuild.Artifact):
		fetchable = fetchable.url
	headers = await get_response_headers(fetchable, max_age=max_age, refresh_interval=refresh_interval)
	res = re.search(r"filename=\"?(\S+)\"?", headers.get("Content-Disposition", ""))
	return None if not res else res.group(1)


async def get_url_from_redirect(fetchable, max_age=None, refresh_interval=None):
	if isinstance(fetchable, pkgtools.ebuild.Artifact):
		fetchable = fetchable.url
	return await fetch_harness(
		pkgtools.http.get_url_from_redirect, fetchable, max_age=max_age, refresh_interval=refresh_interval
	)


# vim: ts=4 sw=4 noet
