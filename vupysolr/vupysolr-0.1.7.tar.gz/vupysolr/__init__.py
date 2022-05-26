"""
Access Solr stored VuFind records.

For more information on VuFind, see
https://vufind.org
"""

__author__ = "Donatus Herre <donatus.herre@slub-dresden.de>"
__version__ = "0.1.7"

from .docs import VuFindParser
from .base import VuFindIndex, VuFindCluster


def parse(doc):
    return VuFindParser(doc)


def index(url="http://localhost:8983/solr", core="biblio", name="default", marc=False, loglevel=0):
    return VuFindIndex(url=url, core=core, name=name, marc=marc, loglevel=loglevel)


def get(id, url="http://localhost:8983/solr", core="biblio", name="default", marc=False, loglevel=0):
    i = index(url=url, core=core, name=name, marc=marc, loglevel=loglevel)
    return i.get(id)


def cluster(meta):
    idx = []
    for i in meta:
        url = None
        core = "biblio"
        name = "default"
        marc = False
        loglevel = 0
        if "url" in i:
            url = i["url"]
        if "core" in i:
            core = i["core"]
        if "name" in i:
            name = i["name"]
        if "marc" in i:
            marc = i["marc"]
        if "loglevel" in i:
            loglevel = i["loglevel"]
        if url is not None:
            idx.append(index(url, core=core, name=name, marc=marc, loglevel=loglevel))
    if len(idx) > 0:
        return VuFindCluster(idx)
