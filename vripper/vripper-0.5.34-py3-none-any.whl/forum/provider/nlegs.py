from commmons import html_from_url, get_host_url

from vripper.model.vimage import VImage
from vripper.model.vthread import VThread


def nlegs_init(url: str):
    root = html_from_url(url)

    thread = VThread(
        id=url.split('/')[-1].split('.')[0],
        title=root.xpath('//title')[0].text,
        with_empty_post=True
    )

    return thread, thread.posts[0], root, url


def nlegs_populate_images(payload):
    thread, post, root, thread_url = payload

    for i, atag in enumerate(root.xpath("//a[@class='thumbnail']")):
        href = atag.attrib["href"]
        image_link = get_host_url(thread_url) + href
        post.images.append(VImage(index_in_post=i, url=image_link))

    assert len(post.images) > 0
    thread.posts.append(post)

    return thread
