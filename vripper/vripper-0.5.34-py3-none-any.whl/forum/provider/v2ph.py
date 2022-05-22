from commmons import html_from_url, md5

from vripper.model.vimage import VImage
from vripper.model.vthread import VThread


def _get_images(root, index_offset):
    for i, img in enumerate(root.xpath("//img[contains(@class,'album-photo')]")):
        url = img.attrib["data-src"]
        yield VImage(index_in_post=index_offset + i, url=url)


def v2ph_init(url):
    root = html_from_url(url)

    # id may contain filesystem-unsafe characters such as the question mark
    hashed_id = md5(url.split("/album/")[-1].split(".")[0].split("?")[0])

    thread = VThread(
        id=hashed_id,
        title=root.xpath("//h1[contains(@class, 'text-center')]")[0].text,
        with_empty_post=True
    )

    return thread, thread.posts[0], root


def v2ph_populate_images(payload):
    thread, post, root = payload

    while root is not None:
        post.images.extend(_get_images(root, index_offset=len(post.images)))

        # full contents are for premium users only
        root = None

    return thread
