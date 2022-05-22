from typing import Tuple

from commmons import html_from_url, head, get_host_url
from lxml.html import HtmlElement

from vripper.model.vimage import VImage
from vripper.model.vpost import VPost
from vripper.model.vthread import VThread


def _collect_images(page, index_offset):
    article = head(page.xpath("//div[@class='article-fulltext']"))
    for i, img in enumerate(article.xpath(".//img")):
        img_url = img.attrib["data-src"]
        yield VImage(index_in_post=index_offset + i, url=img_url)


def _get_next_href(page):
    pagination = head(page.xpath("//div[@class='pagination-list']"))
    if pagination is not None:
        found_current_page = False
        atags = pagination.xpath(".//a")
        for a in atags:
            is_current = "is-current" in a.attrib["class"]
            if is_current:
                found_current_page = True
                continue
            elif found_current_page:
                return a.attrib["href"]
    return None


def buondua_init(url: str):
    first_page = html_from_url(url)
    title = head(first_page.xpath("//div[@class='article-header']/h1")).text
    thread = VThread(title=title, url=url, with_empty_post=True)
    return thread, thread.posts[0], first_page


def buondua_collect_pages(payload: Tuple[VThread, VPost, HtmlElement]) -> VThread:
    thread, post, page = payload

    post.images.extend(_collect_images(page, len(post.images)))

    next_href = _get_next_href(page)
    if next_href is not None:
        page = html_from_url(get_host_url(thread.url) + next_href)
        return buondua_collect_pages((thread, post, page,))

    return thread
