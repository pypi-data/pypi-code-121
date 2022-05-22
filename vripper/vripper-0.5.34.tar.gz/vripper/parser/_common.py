import requests
from lxml import html

from vripper.error import ImagePermanentlyUnavailableError

_MAX_DEPTH = 5


def get_form_data(tree) -> dict:
    inputs = tree.xpath("//form//input")
    return {
        i.attrib["name"]: i.attrib["value"] for i in inputs
        if "name" in i.attrib and "value" in i.attrib
    }


def parse(url, timeout, xpath_expr, attr="src", unavailable_phrase=None, post_callback=None):
    r = requests.get(url, timeout=timeout)
    if r.status_code == 404:
        raise ImagePermanentlyUnavailableError
    r.raise_for_status()

    def default_post_callback(t):
        payload = get_form_data(t)
        return requests.post(url, payload, headers={"Referer": url}, timeout=timeout)

    for i in range(_MAX_DEPTH):
        if unavailable_phrase and unavailable_phrase in r.text:
            raise ImagePermanentlyUnavailableError

        tree = html.fromstring(r.text)
        target_nodes = tree.xpath(xpath_expr)
        if target_nodes:
            assert len(target_nodes) == 1
            return target_nodes[0].attrib[attr]

        pcb = post_callback or default_post_callback
        r = pcb(tree)
        r.raise_for_status()

    raise RuntimeError
