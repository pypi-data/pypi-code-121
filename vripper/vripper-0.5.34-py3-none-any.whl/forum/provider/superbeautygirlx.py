from commmons import html_from_url

from vripper.model.vimage import VImage
from vripper.model.vthread import VThread


def sbgx_init(url):
    root = html_from_url(url)

    content = root.xpath("//div[contains(@class, 'post-body') and contains(@class, 'entry-content')]")[0]

    thread = VThread(
        id=content.attrib["id"].lstrip("post-body-"),
        title=root.xpath("//h1[contains(@class, 'post-title')]")[0].text,
        with_empty_post=True
    )

    return thread, thread.posts[0], content


def sbgx_populate_images(payload):
    thread, post, content = payload

    for i, div in enumerate(content.xpath(".//div[@class='separator']")):
        imgs = div.xpath('.//img')
        if imgs:
            img_url = imgs[0].attrib["src"]
            post.images.append(VImage(index_in_post=i, url=img_url))

    thread.posts.append(post)

    return thread
