import os
import requests
import time
import xml.dom.minidom as md
from pypers.utils import xmldom
from pypers.utils import utils
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract BGTM archives
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]}

    def preprocess(self):
        self.xml_data_map = {"AP": {}, "RE": {}}
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
        # self.archives is a tuple of (date, {archive_name: xxx, archives[]})

        if not len(self.archives):
            return

        extraction_date = self.archives[0]
        archive_name = self.archives[1]['name']
        archives = self.archives[1]['archives']
        # prepare destination dir under pipeline scratch dir
        self.extraction_dir = os.path.join(
            self.meta['pipeline']['output_dir'],
            '__scratch',
            extraction_date,
            archive_name
        )

        # deletes the directory if prev exists
        utils.mkdir_force(self.extraction_dir)

        self.manifest = {'archive_name': archive_name,
                         'archive_file': archive_name,
                         'archive_date': extraction_date,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}
        for archive in archives:
            extraction = os.path.join(self.extraction_dir, os.path.basename(archive))
            self.collect_files(self.unpack_archive(archive, extraction))


    def add_xml_file(self, filename, fullpath):
        if filename.endswith('500000000000000.xml'):
            return
        proxy_params = self.get_connection_params()
        # open a session to download missing applicants and representatives
        with requests.session() as session:
            # happens that the data file is empty :(
            try:
                xmldom.clean_xmlfile(fullpath, overwrite=True)
            except:
                self.logger.info('[%s] bypassing' % filename)
                return
            mark_dom = md.parse(fullpath)
            appnum = xmldom.get_nodevalue('ApplicationNumber', dom=mark_dom)

            mark_fname = os.path.join(self.extraction_dir, '%s.xml' % appnum)

            # -----------------------------------------------
            # Getting Applicants from URI
            # -----------------------------------------------
            data_app_node = mark_dom.getElementsByTagName('ApplicantDetails')

            # get applicant from URI and replace the node in xml
            for details_node in data_app_node:
                entity_nodes = details_node.getElementsByTagName('Applicant')
                for entity_node in entity_nodes:
                    entity_uri = xmldom.get_nodevalue('ApplicantURI', dom=entity_node)

                    time.sleep(.1)
                    response = session.get(entity_uri, proxies=proxy_params)
                    if response.status_code == 404:
                        print('[%s] Could not download applicant [%s]' % (appnum, entity_uri))
                        continue

                    entity_dom = md.parseString(response.content)

                    entity_node_from_request = entity_dom.getElementsByTagName('Applicant')
                    # replace old one by the new one
                    if len(entity_node_from_request):
                        details_node.removeChild(entity_node)
                        details_node.appendChild(entity_node_from_request[0])

            # -----------------------------------------------
            # Getting Representatives from URI
            # -----------------------------------------------
            data_rep_node = mark_dom.getElementsByTagName('RepresentativeDetails')
            for details_node in data_rep_node:
                entity_nodes = details_node.getElementsByTagName('Representative')
                for entity_node in entity_nodes:
                    entity_uri = xmldom.get_nodevalue('RepresentativeURI', dom=entity_node)

                    time.sleep(.1)
                    response = session.get(entity_uri, proxies=proxy_params)
                    if response.status_code == 404:
                        print('[%s] Could not download rep [%s]' % (appnum, entity_uri))
                        continue

                    entity_dom = md.parseString(response.content)

                    entity_node_from_request = entity_dom.getElementsByTagName('Representative')
                    # replace old one by the new one
                    if len(entity_node_from_request):
                        details_node.removeChild(entity_node)
                        details_node.appendChild(entity_node_from_request[0])
            xmldom.save_xml(
                mark_dom, mark_fname, newl='\n', addindent='  ')

            mark_img = mark_dom.getElementsByTagName('MarkImageURI')
            img_uri = None
            if len(mark_img):
                img_uri = mark_img[0].firstChild.nodeValue

            os.remove(fullpath)
            self.manifest['data_files'].setdefault(appnum, {})
            self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                mark_fname, self.extraction_dir
            )
            if img_uri:
                self.add_img_url(appnum, img_uri)



    def process(self):
        pass