import os
import shutil
import time
import requests
import xml.dom.minidom as md
from pypers.utils import xmldom
from pypers.utils import utils
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract ITTM archives
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "input_files",
                    "type": "file",
                    "descr": "the files to extract"
                }
            ]
        }
    }

    def preprocess(self):
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
        # self.archives is a tuple of (date, file)

        if not len(self.archives):
            return

        extraction_date = self.archives[0]
        archive = self.archives[1]

        archive_name, _ = os.path.splitext(os.path.basename(archive))

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
                         'archive_file': archive,
                         'archive_date': extraction_date,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}


        # unpack the archives and collect the files
        self.process_csv(archive)

    def process(self):
        pass

    def process_csv(self, archive):
        url = 'http://tmview.uibm.gov.it/trademark/data/IT%s'
        proxy_params = self.get_connection_params()

        with requests.session() as session, open(archive, 'r') as fh:
            for line in fh:
                line = line.rstrip()

                if not line.startswith('30'):
                    self.logger.info('\tskipping line %s' % line)
                    continue

                line = line.split(',')[0]

                appid = line
                appnum = line[2:]

                mark_fname = os.path.join(self.extraction_dir, '%s.xml' % appnum)

                response = session.get(url % appid, proxies=proxy_params)

                try:
                    mark_str = ''.join(c for c in response.content.decode('utf-8') if ord(c) >= 32)
                    mark_dom = md.parseString(mark_str)

                    data_app_node = mark_dom.getElementsByTagName(
                        'ApplicantKey')
                    data_rep_node = mark_dom.getElementsByTagName(
                        'RepresentativeKey')
                    if len(mark_dom.getElementsByTagName('exceptionVO')):
                        self.logger.error('ERROR for %s' % (url % appid))
                        continue

                    for applicant_node in data_app_node:
                        applicant_uri = xmldom.get_nodevalue(
                            'URI', dom=applicant_node)
                        time.sleep(.1)
                        response = session.get(applicant_uri,
                                               proxies=proxy_params)
                        applicant_dom = md.parseString(response.content)

                        app_node = applicant_dom.getElementsByTagName(
                            'Applicant')
                        if len(app_node):
                            applicant_node.appendChild(app_node[0])

                    for representative_node in data_rep_node:
                        representative_uri = xmldom.get_nodevalue(
                            'URI', dom=representative_node)

                        time.sleep(.1)
                        response = session.get(representative_uri,
                                               proxies=proxy_params)
                        representative_dom = md.parseString(
                            response.content)
                        rep_node = representative_dom.getElementsByTagName(
                            'Representative')
                        if len(rep_node):
                            representative_node.appendChild(rep_node[0])

                    xmldom.save_xml(mark_dom, mark_fname,
                                    addindent='  ', newl='\n')

                    self.add_xml_file(appnum, mark_fname)
                    mark_img = mark_dom.getElementsByTagName('MarkImageURI')
                    if not len(mark_img):
                        self.logger.info('%s - %s' % (appnum, ''))
                    else:
                        mark_img_uri = mark_img[0].firstChild.nodeValue
                        self.add_img_url(appnum, mark_img_uri)
                        self.logger.info('%s - %s' % (appnum, mark_img_uri))
                except Exception as e:
                    self.logger.error('ERROR reading XML %s' % appid)
                    self.logger.error(mark_str)
                    continue
