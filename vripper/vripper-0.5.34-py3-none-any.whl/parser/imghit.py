import requests

from vripper.parser._common import parse
from vripper.parser._def import parser


@parser("imghit", is_active=False)
def p(url, timeout):
    def pcb(tree):
        form_nodes = tree.xpath("//*[@id='form-captcha']")
        assert len(form_nodes) == 1

        input_nodes = form_nodes[0].xpath("//input")
        payload = {i.attrib["name"]: i.attrib["value"] for i in input_nodes}
        return requests.post(url, payload, timeout=timeout)

    return parse(url, timeout, "//img", post_callback=pcb)
