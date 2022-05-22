import requests

from vripper.parser._common import parse
from vripper.parser._def import parser


@parser("imgclick")
def p(url, timeout):
    def pcb(tree):
        input_nodes = tree.xpath("//form[@id='form-captcha']/input")
        payload = {i.attrib["name"]: i.attrib["value"] for i in input_nodes}
        return requests.post(url, payload, timeout=timeout)

    return parse(
        url, timeout, xpath_expr="//img[@class='pic']", post_callback=pcb,
        unavailable_phrase="The file you were looking for could not be found"
    )
