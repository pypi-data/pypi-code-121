'''
Copyright (c) 2020 by Windward Studios, Inc. All rights reserved.
This software is the confidential and proprietary information of
Windward Studios ("Confidential Information").  You shall not
disclose such Confidential Information and shall use it only in
accordance with the terms of the license agreement you entered into
with Windward Studios, Inc.
'''


from windwardrestapi.Model import Document, DocumentMeta
from windwardrestapi.Model import Template, TagTree, VersionInfo, Metrics
import requests
import logging

_HEADERS = {'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json'}
_DOCUMENT_PATH = "v2/document"
_VERSION_PATH = "v2/version"
_METRICS_PATH = "v2/metrics"
_TAGTREE_PATH = "v2/tagtree"

class WindwardClient(object):

    def __init__(self, urlHost, licenseKey=None):
        self.headers = _HEADERS
        self._baseUri = None
        self._licenseKey = None
        logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
        logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

        if urlHost is not None:
            if not urlHost.endswith('/'):
                self.baseUri = urlHost + '/'
            else:
                self.baseUri = urlHost
        if licenseKey is not None:
            self.licenseKey = licenseKey

    @property
    def baseUri(self):
        return self._baseUri

    @baseUri.setter
    def baseUri(self, base_uri):
        self._baseUri = base_uri

    @property
    def licenseKey(self):
        return self._licenseKey

    @licenseKey.setter
    def licenseKey(self, license_key):
        self.headers.update({"X-WINDWARD-LICENSE" : license_key})
        self._licenseKey = license_key

    def getVersion(self):
        try:
            versionUri = self._baseUri + _VERSION_PATH
            response = requests.get(versionUri, headers=self.headers)
            try:
                response.raise_for_status()
            except requests.exceptions as httpError:
                logging.exception("Error getting version info:", exc_info=httpError)
                raise
            return VersionInfo.VersionInfo(response)
        except Exception:
            logging.exception("getVersion() throws ", exc_info=True)
            raise

    def postDocument(self, template):
        try:
            documentUri = self._baseUri + _DOCUMENT_PATH

            if not isinstance(template, dict):
                template = template.toDict()
            request = requests.post(documentUri,  headers=self.headers, json=template)
            try:
                request.raise_for_status()
            except requests.exceptions.HTTPError as httpError:
                logging.exception("Error posting template", exc_info=httpError)
                raise

            response = request.json()

            return Document.Document(response)
        except Exception:
            logging.exception("postDocument() throws: ", exc_info=True)
            raise

    def getDocumentStatus(self, guid):
        try:
            getDocumentUri = self._baseUri + _DOCUMENT_PATH + '/' + guid + '/status'
            status = requests.get(getDocumentUri)
            return status.status_code
        except Exception:
            logging.exception("getDocumentStatus() ", + guid + " throws: ", exc_info=True)
            raise

    def getDocument(self, guid):
        try:
            getDocumentUri = self._baseUri + _DOCUMENT_PATH + '/' + guid
            response = requests.get(getDocumentUri, headers=self.headers)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as httpError:
                logging.exception("Error getting document with Guid="+guid, exc_info=httpError)
                raise
            responseDict = response.json()
            return Document.Document(responseDict)
        except Exception:
            logging.exception("getDocument() " + guid + " throws: ", exc_info=True)
            raise


    def getDocumentMeta(self, guid):
        try:
            getDocumentUri = self._baseUri + _DOCUMENT_PATH + '/' + guid + '/meta'
            response = requests.get(getDocumentUri, headers=self.headers)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as httpError:
                logging.exception("Error getting document with Guid="+guid, exc_info=httpError)
                raise
            responseDict = response.json()
            return DocumentMeta.DocumentMeta(responseDict)
        except Exception:
            logging.exception("getDocument() ", + guid + " throws: ", exc_info=True)
            raise

    def getDocumentFile(self, guid):
        try:
            getDocumentUri = self._baseUri + _DOCUMENT_PATH + '/' + guid + '/file'
            response = requests.get(getDocumentUri, headers=self.headers)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as httpError:
                logging.exception("Error getting document with Guid=" + guid, exc_info=httpError)
                raise
            responseStream = response.content
            return responseStream
        except Exception:
            logging.exception("getDocument() ", + guid + " throws: ", exc_info=True)
            raise

    def deleteDocument(self, guid):
        try:
            deleteDocumentUri = self._baseUri + _DOCUMENT_PATH + '/' + guid
            response = requests.delete(deleteDocumentUri)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as httpError:
                logging.exception("Error deleting document, Guid="+guid, exc_info=httpError)
                raise
            logging.info("Deleted document with Guid="+guid)
            return response.status_code
        except Exception:
            logging.exception("deleteDocument() ", + guid + " throws: ", exc_info=True)
            raise

    def postMetrics(self, template):
        try:
            metricsUri = self._baseUri + _METRICS_PATH

            if not isinstance(template, dict):
                template = template.toDict()
            request = requests.post(metricsUri, headers=self.headers, json=template)
            try:
                request.raise_for_status()
            except requests.exceptions.HTTPError as httpError:
                logging.exception("Error posting metrics for template with tag: "+ template.tag, exc_info=httpError)
                raise
            response = request.json()

            return Metrics.Metrics(response)
        except Exception:
            logging.exception("postMetrics() ", + template.tag + " throws: ", exc_info=True)
            raise

    def getMetricsStatus(self, guid):
        try:
            getMetricsStatusUri = self._baseUri + _METRICS_PATH + '/' + guid + '/status'
            status =  requests.get(getMetricsStatusUri)
            return status.status_code
        except Exception:
            logging.exception("getMetricsStatus() ", + guid + " throws: ", exc_info=True)
            raise

    def getMetrics(self, guid):
        try:
            getMetricsUri = self._baseUri + _METRICS_PATH + '/' + guid

            response = requests.get(getMetricsUri, headers=self.headers)
            if response.status_code == requests.codes.ok:
                response = response.json()

            return Metrics.Metrics(response)
        except Exception:
            logging.exception("getMetrics() " + guid + " throws: ", exc_info=True)
            raise

    def deleteMetrics(self, guid):
        try:
            deleteMetricsUri = self._baseUri + _METRICS_PATH + '/' + guid
            response = requests.delete(deleteMetricsUri)
            return response.status_code
        except:
            logging.exception("deleteMetrics() " + guid + " throws: ", exc_info=True)
            raise

    def postTagTree(self, template):
        try:
            tagTreeUri = self._baseUri + _TAGTREE_PATH

            if not isinstance(template, dict):
                template = template.toDict()

            request = requests.post(tagTreeUri, headers=_HEADERS, json=template)
            response = request.json()
            return TagTree.TagTree(response)
        except Exception:
            logging.exception("postTagTree() " + template.tag + " throws: ", exc_info=True)
            raise

    def getTagTreeStatus(self, guid):
        try:
            tagTreeStatus = self._baseUri + _TAGTREE_PATH + '/' + guid
            status = requests.get(tagTreeStatus)
            return status.status_code
        except Exception:
            logging.exception("getTagTreeStatus() " + guid + " throws: ", exc_info=True)
            raise

    def getTagTree(self, guid):
        try:
            getTagTreeUri = self._baseUri + _TAGTREE_PATH + '/' + guid

            response = requests.get(getTagTreeUri, headers=self.headers)
            if response.status_code == requests.codes.ok:
                response = response.json()

            return TagTree.TagTree(response)
        except Exception:
            logging.exception("getTagTree() " + guid + " throws: ", exc_info=True)
            raise

    def deleteTagTree(self, guid):
        try:
            deleteTagTreeUri = self._baseUri + _TAGTREE_PATH + '/' + guid
            response = requests.delete(deleteTagTreeUri)
            return response.status_code
        except:
            logging.exception("deleteTagTree() " + guid + " throws: ", exc_info=True)
            raise

    # def nullSetter(self, response, classType):
    #     for entry in response:
