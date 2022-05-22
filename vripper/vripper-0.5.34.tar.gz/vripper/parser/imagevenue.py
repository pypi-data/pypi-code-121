import requests
from lxml import html

from vripper.parser._def import parser


@parser("imagevenue")
def p(url, timeout):
    r = requests.get(url, timeout=timeout)
    tree = html.fromstring(r.text)

    img_nodes = tree.xpath("//img")
    for img in img_nodes:
        if "alt" in img.attrib:
            return img.attrib["src"]

    raise RuntimeError
