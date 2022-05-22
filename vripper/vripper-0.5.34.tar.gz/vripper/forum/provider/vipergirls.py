import urllib.parse as urlparse
import xml.etree.ElementTree as ET

import requests
from commmons import get_query_param, strip_query_params

from vripper.model.vimage import VImage
from vripper.model.vpost import VPost
from vripper.model.vthread import VThread

_API_BASE_URL = "https://vipergirls.to/vr.php"


def _check_permissions(root):
    error = root.find("error")
    if error is not None and error.attrib["type"] == "permissions":
        raise PermissionError(error.attrib["details"])


def _populate_images(post, post_element):
    for i, img_node in enumerate(post_element.findall("image")):
        img = VImage(index_in_post=i, url=img_node.attrib["main_url"], thumb_url=img_node.attrib.get("thumb_url"))
        post.images.append(img)


def vg_get_xml(url):
    thread = VThread()
    thread.id = url.split('/')[-1].split('-')[0]

    params = {"t": thread.id}
    postid = get_query_param(url, "p")
    if postid:
        params = {"p": postid}

    r = requests.get(_API_BASE_URL, params)
    r.raise_for_status()

    root = ET.fromstring(r.text)
    _check_permissions(root)

    t = root.find("thread")
    thread.title = t.attrib["title"]
    thread.url = strip_query_params(url)
    reply_index = get_query_param(url, "r")
    if reply_index:
        thread.id += f"-r{reply_index}"
        thread.title += f" Reply {reply_index}"

    return thread, root, reply_index, postid


def vg_process(payload):
    thread, root, reply_index, postid = payload

    for i, post_element in enumerate(root.findall("post")):
        if reply_index is not None and i != int(reply_index):
            continue

        post = VPost()
        post.id = post_element.attrib["id"]
        post.url = f"{thread.url}?{urlparse.urlencode({'p': post.id})}"
        post.title = thread.title
        if postid:
            post.title += f" Post {postid}"
            thread.title = post.title

        _populate_images(post, post_element)

        thread.posts.append(post)

    return thread
