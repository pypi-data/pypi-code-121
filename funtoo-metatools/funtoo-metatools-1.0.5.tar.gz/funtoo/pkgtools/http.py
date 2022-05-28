#!/usr/bin/env python3

import logging

import dyne.org.funtoo.metatools.pkgtools as pkgtools
import httpx

from metatools.fastpull.spider import FetchRequest, FetchError

"""
This sub implements lower-level HTTP fetching logic, such as actually grabbing the data, sending the
proper headers and authentication, etc.
"""


def set_basic_auth(request: FetchRequest):
	"""
	Keyword arguments to get_page() GET requests for authentication to certain URLs based on configuration
	in ~/.autogen (YAML format.)
	"""
	if "authentication" in pkgtools.model.config:
		if request.hostname in pkgtools.model.config["authentication"]:
			auth_info = pkgtools.model.config["authentication"][request.hostname]
			request.set_auth(**auth_info)


async def get_page(url, encoding=None, is_json=False):
	"""
	This function performs a simple HTTP fetch of a resource. The response is cached in memory,
	and a decoded Python string is returned with the result. FetchError is thrown for an error
	of any kind.

	Use ``encoding`` if the HTTP resource does not have proper encoding and you have to set
	a specific encoding. Normally, the encoding will be auto-detected and decoded for you.
	"""
	request = FetchRequest(url=url)
	set_basic_auth(request)
	# Leverage the spider for this fetch. This bypasses the FPOS, etc:
	result = await pkgtools.model.spider.http_fetch(request, encoding=encoding, is_json=is_json)
	return result


async def get_url_from_redirect(url):
	"""
	This function will take a URL that redirects and grab what it redirects to. This is useful
	for /download URLs that redirect to a tarball 'foo-1.3.2.tar.xz' that you want to download,
	when you want to grab the '1.3.2' without downloading the file (yet).
	"""
	logging.info(f"Getting redirect URL from {url}...")
	async with httpx.AsyncClient() as client:
		try:
			resp = await client.get(url=url, follow_redirects=False)
			if resp.status_code == 302:
				return resp.headers["location"]
		except httpx.RequestError as e:
			raise FetchError(url, f"Couldn't get_url_from_redirect due to exception {repr(e)}")


async def get_response_headers(url):
	"""
	This function will take a URL and grab its response headers. This is useful for obtaining
	information about a URL without fetching its body.
	"""
	async with httpx.AsyncClient() as client:
		resp = await client.get(url=url, follow_redirects=True)
		return resp.headers


# vim: ts=4 sw=4 noet
