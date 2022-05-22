from commmons import html_from_url

from vripper.model.vimage import VImage
from vripper.model.vthread import VThread


def thm_init(url):
    root = html_from_url(url)

    thread = VThread(
        id=root.xpath("//article[contains(@class, 'post')]")[0].attrib["id"],
        title=root.xpath("//h1[@class='entry-title']")[0].text,
        with_empty_post=True
    )

    return thread, thread.posts[0], root


def thm_populate_images(payload):
    thread, post, root = payload

    imgs = root.xpath("//div[@class='entry-content']//img[contains(@class, 'jetpack-lazy-image')]")
    for i, img in enumerate(imgs):
        url = img.attrib["src"].split("?")[0]
        image = VImage(index_in_post=i, url=url)
        post.images.append(image)

    return thread
