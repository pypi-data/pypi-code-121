#!/usr/bin/env python3

from bs4 import BeautifulSoup
from packaging import version

"""
```pkgtools.pages`` contains useful functions for iterating over HTML pages and extracting
data, as well as handling versions.
"""


async def iter_links(base_url=None, match_fn=None, fixup_fn=None, first_match=False):
	"""
	This method will, given URL ``base_url``, fetch the page and parse it as HTML, and
	iterate over each link in the page that has a ``href``.

	``match_fn`` is a lambda or function that will be passed each ``href`` string, and
	should return None if a match is not found, and a non-None value if a match is found.
	All non-None values will be appended to the result list returned to the caller.

	``fixup_fn`` is a lambda or function that if specified will be used to "fix up" or
	"clean" the result of ``match_fn`` before it is returned.

	A list of matches will be returned if ``first_match`` is False. If ``first_match``
	is true (useful for regexes), then the first match will be returned, or None if
	no match was found.

	Here are some example usages::

	  versions = await hub.pkgtools.pages.grab_links(hub,
	    base_url=f"http://ck.kolivas.org/patches/{major_ver}.0/",
		match_fn=lambda x: x if x.startswith(major_ver) else None,
		fixup_fn=lambda x: x.rstrip("/")
	  )

	Above, we will find hrefs that begin with the major_ver, and for any matches, the
	string will be cleaned to remove trailing slashes.

	Here is another example, using a regex::

	  patch_versions = await hub.pkgtools.pages.grab_links(hub,
	    base_url=f"https://mirrors.edge.kernel.org/pub/linux/kernel/v{major_ver}.x/",
		match_fn=lambda x: re.match(f"patch-{major_ver}\.{minor_ver}\.([0-9+]).xz", x),
		fixup_fn=lambda x: x.groups()[0]
	  )

	Above, we find use a regex to match hrefs, and the fixup function ensures we get
	a list of version strings rather than the actual regex match object.

	"""
	outs = []
	dl_data = await hub.pkgtools.fetch.get_page(base_url, is_json=False)
	dl_soup = BeautifulSoup(dl_data, "lxml")
	for a in dl_soup.find_all("a", href=True):
		match = match_fn(a["href"])
		if match:
			if fixup_fn:
				outs.append(fixup_fn(match))
			else:
				outs.append(match)
			if first_match:
				return outs[0]
	if first_match:
		return None
	return outs


def latest(items, dict_key=None, attr=None):
	"""
	Latest will iterate over ``items`` and use ``version.parse`` to find the
	latest version of the provided strings.

	You can also provide arbitrary objects and specify ``attr`` to point to
	the name of an attribute for comparison, or pass dicts and use ``dict_key``
	to specify a dictionary key to be used to look up a value for comparisons.

	The latest version will be returned, or None if the list of items was
	empty.
	"""
	if not len(items):
		return None
	if dict_key is None and attr is None:
		return max(items, key=lambda x: version.parse(x))
	elif dict_key is not None and attr is not None:
		raise AttributeError("Specify either dict_key or attr for latest()")
	elif dict_key:
		return max(items, key=lambda x: version.parse(x.get(dict_key)))
	else:
		return max(items, key=lambda x: version.parse(getattr(x, attr)))
