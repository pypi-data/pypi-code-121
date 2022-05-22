from functools import reduce
from typing import List

from requests import HTTPError

from vripper.error import ImagePermanentlyUnavailableError
from vripper.forum.provider.buondua import buondua_init, buondua_collect_pages
from vripper.forum.provider.dirtyship import dirtyship_get_images, dirtyship_init
from vripper.forum.provider.nlegs import nlegs_init, nlegs_populate_images
from vripper.forum.provider.superbeautygirlx import sbgx_init, sbgx_populate_images
from vripper.forum.provider.thaihotmodels import thm_init, thm_populate_images
from vripper.forum.provider.v2ph import v2ph_init, v2ph_populate_images
from vripper.forum.provider.vipergirls import vg_get_xml, vg_process
from vripper.model.vpost import GalleryAsVPost
from vripper.model.vthread import VThread

# TODO: use decorator
_FORUM_REGISTRY = [
    (("vipergirls",), (vg_get_xml, vg_process)),
    (("nlegs", "uuleg", "honeyleg", "legbabe", "leg.cx"), (nlegs_init, nlegs_populate_images)),
    (("superbeautygirlx",), (sbgx_init, sbgx_populate_images)),
    (("v2ph.com",), (v2ph_init, v2ph_populate_images)),
    (("thaihotmodels",), (thm_init, thm_populate_images)),
    (("buondua",), (buondua_init, buondua_collect_pages)),
    (("dirtyship",), (dirtyship_init, dirtyship_get_images))
]


def chain(payload, func):
    return func(payload)


def _get_function_chain_by_url(url):
    for entry in _FORUM_REGISTRY:
        pattern: List[str] = entry[0]
        funcs = entry[1]
        if any(map(lambda substr: substr in url, pattern)):
            return funcs

    return None


def get_thread(url: str) -> VThread:
    funcs = _get_function_chain_by_url(url)

    if funcs:
        try:
            thread = reduce(chain, funcs, url)
        except HTTPError as e:
            if e.response.status_code in (403, 404):
                raise ImagePermanentlyUnavailableError(str(e))
            raise
        assert isinstance(thread, VThread)
    else:
        # IF the website is not supported, then fallback to GalleryDL
        post = GalleryAsVPost(url)
        thread = VThread()
        thread.posts.append(post)

    return thread
