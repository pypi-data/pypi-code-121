from typing import Tuple, List

from commmons import html_from_url, head, md5
from lxml.html import HtmlElement

from vripper.model.vimage import VImage
from vripper.model.vpost import VPost
from vripper.model.vthread import VThread


def sort_by_url(atags: List[HtmlElement]):
    def sanitize(a) -> int:
        maybe_int = a.attrib["href"].strip("/").split("-")[-1]
        try:
            return int(maybe_int)
        except ValueError:
            return 0

    return sorted(atags, key=lambda a: sanitize(a))


def dirtyship_init(url: str):
    root = html_from_url(url)

    t = VThread(id=md5(url), url=url, with_empty_post=True)

    h1 = head(root.xpath("//div[@class='content-title']//h1"))
    if h1 is None:
        t.title = h1.text

    return root, t, t.posts[0]


def dirtyship_get_images(payload: Tuple[HtmlElement, VThread, VPost]):
    root, thread, post = payload

    sorted_atgs = sort_by_url(root.xpath("//div[@class='gallery_grid']/a"))
    for i, atag in enumerate(sorted_atgs):
        url = atag.attrib["href"]
        image = VImage(index_in_post=i, url=url)
        post.images.append(image)

    return thread
