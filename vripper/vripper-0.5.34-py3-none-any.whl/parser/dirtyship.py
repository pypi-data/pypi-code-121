from commmons import html_from_url

from vripper.parser._def import parser


@parser("dirtyship")
def p(url: str, timeout):
    root = html_from_url(url, timeout=timeout)
    for atag in root.xpath("//div[@class='resolutions']//a"):
        if "full" in atag.text:
            return atag.attrib["href"]

    raise RuntimeError
