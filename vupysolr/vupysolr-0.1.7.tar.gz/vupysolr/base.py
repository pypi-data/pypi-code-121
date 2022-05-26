"""
Access Solr based VuFind indexes.
"""

import pysolr
import pymarc
import logging

from .docs import VuFindParser
from .utils import get_logger, json_req


class VuFindIndex:

    def __init__(self, url="http://localhost:8983/solr", core="biblio", name="default", marc=False, loglevel=logging.WARNING):
        self.url = url.strip("/")
        self.core = core
        self.name = name
        self.marc = marc
        self.url_core = "{0}/{1}".format(self.url, self.core)
        self.url_schema = "{0}/{1}".format(self.url_core, "schema")
        self.url_config = "{0}/{1}".format(self.url_core, "config")
        self.url_status = "{0}/admin/cores?action=STATUS&core={1}&wt=json".format(self.url, self.core)
        self.client = pysolr.Solr(self.url_core)
        self.logger = get_logger("vupysolr", loglevel=loglevel)

    def _get(self, id, post=None):
        self.logger.info("Fetch document with id {0} from Solr index {1}.".format(id, self.name))
        response = self.search(self.query_id(id))
        if response is not None:
            if response.hits == 1:
                document = response.docs[0]
                if post is not None:
                    document = post(document)
                return document
            else:
                if response.hits == 0:
                    self.logger.warning("No document found with id {0} in VuFind Solr index {1}.".format(id, self.name))
                elif response.hits > 1:
                    self.logger.warning("Multiple documents found with id {0} in VuFind Solr index {1}.".format(id, self.name))

    def get(self, id):
        if self.marc:
            document = self._get(id, post=self.decode_marc)
        else:
            document = self._get(id)
        if document is not None:
            return VuFindParser(document, marc=self.marc)

    def search(self, query, search_handler=None, **kwargs):
        try:
            return self.client.search(query, search_handler=search_handler, **kwargs)
        except pysolr.SolrError as err:
            self.logger.exception(err)
            self.logger.error("Request of query '{0}' failed!".format(query))

    def find_doc(self, query, **kwargs):
        response = self.search(query, **kwargs)
        if response is not None:
            if len(response.docs) > 0:
                if len(response.docs) == 1:
                    return response.docs[0]
                else:
                    self.logger.warning("Found multiple documents matching query {0}".format(query))

    def find_id(self, query):
        document = self.find_doc(query, fl="id")
        if document is not None and "id" in document:
            return document["id"]

    @staticmethod
    def query(key, value):
        return "{0}:{1}".format(key, value)

    def query_id(self, id):
        return self.query("id", '"{0}"'.format(id))

    def id_in_index(self, id):
        document = self.find_doc(self.query_id(id))
        if document is not None:
            return True
        return False

    def schema(self):
        response = json_req(self.url_schema)
        if response is not None:
            if "schema" in response:
                return response["schema"]

    def config(self):
        response = json_req(self.url_config)
        if response is not None:
            if "config" in response:
                return response["config"]

    def status(self):
        response = json_req(self.url_status)
        if response is not None:
            if "status" in response:
                if self.core in response["status"]:
                    return response["status"][self.core]

    def set_loglevel(self, level):
        if self.logger.level != level:
            self.logger.setLevel(level)
        if self.logger.handlers:
            for handler in self.logger.handlers:
                handler.setLevel(level)

    def decode_marc(self, document):
        if "fullrecord" in document:
            marcdata = document["fullrecord"].encode("utf-8")
            try:
                document["fullrecord"] = pymarc.Record(data=marcdata).as_dict()
            except pymarc.exceptions.PymarcException as err:
                doc_id = None
                if "id" in document:
                    doc_id = document["id"]
                self.logger.exception(err)
                if doc_id is not None:
                    self.logger.error("Parsing MARC data of document '{0}' failed!".format(doc_id))
        return document


class VuFindCluster:

    def __init__(self, idx=None):
        self.idx = []
        if type(idx) == VuFindIndex:
            self.idx.append(idx)
        elif type(idx) == list:
            self.idx = idx

    def find_index(self, id):
        for idx in self.idx:
            if idx.id_in_index(id):
                return idx.name

    def get_index(self, name):
        for idx in self.idx:
            if idx.name == name:
                return idx

    def get(self, id):
        for idx in self.idx:
            if idx.id_in_index(id):
                doc = idx.get(id)
                if doc is not None:
                    return doc

    def get_from_index(self, id, name):
        for idx in self.idx:
            if idx.name == name:
                doc = idx.get(id)
                if doc is not None:
                    return doc

    def set_loglevel(self, level):
        for idx in self.idx:
            idx.set_loglevel(level)
