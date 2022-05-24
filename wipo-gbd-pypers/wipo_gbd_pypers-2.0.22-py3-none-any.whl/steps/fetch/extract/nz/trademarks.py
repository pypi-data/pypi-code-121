import os
import glob
import requests
import base64
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
from pypers.utils.xmldom import save_xml
from pypers.utils.download import retry
from pypers.utils import utils
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract NZTM marks information from api
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
                    "name": "api_details",
                    "type": "str",
                    "descr": "the api endpoint to extract mark xml details"
                },
                {
                    "name": "api_image",
                    "type": "str",
                    "descr": "the api endpoint to extract mark image"
                }
            ]
        }
    }

    # initializes the outputs
    def preprocess(self):
        self._get_connection()
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
        self.manifest = {
            'data_files': {},
            'img_files': {},
            'media_files': {}
        }
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
        utils.mkdir_force(os.path.join(self.extraction_dir, 'xml'))
        utils.mkdir_force(os.path.join(self.extraction_dir, 'img'))

        self.manifest = {'archive_name': archive_name,
                         'archive_file': archive,
                         'archive_date': extraction_date,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}

        # unpack the archives and collect the files
        self.collect_files(archive)


    def get_application(self, session, appnum):

        @retry(Exception, tries=6, delay=3, backoff=2)
        def _get_application(session, url, proxies=None, headers=None):
            response = session.get(url, proxies=proxies, headers=headers)
            return response.content

        try:
            design_xml = _get_application(
                session, self.api_details_url % appnum,
                proxies=self.proxy_params, headers=self.headers_det)
            design_dom = md.parseString(design_xml)
            return design_dom
        except Exception as e:
            self.logger.error(appnum)
            return None

    def _get_connection(self):
        fetch_from = self.meta['pipeline']['input']
        conn_params = fetch_from['from_api']
        self.proxy_params = {
            'http': self.meta['pipeline']['input'].get('http_proxy', None),
            'https': self.meta['pipeline']['input'].get('https_proxy', None)
        }

        self.headers_img = {
            'Authorization': 'Bearer %s' % conn_params['token'],
            'content-type': 'text/xml; charset=utf-8',
            'SOAPAction': 'getDocument'}
        self.headers_det = {'Authorization': 'Bearer %s' % conn_params['token']}

        self.api_details_url = os.path.join(conn_params['url'],
                                            self.api_details)
        self.api_image_url = os.path.join(conn_params['url'], self.api_image)

    def get_image(self, session, post_data):
        @retry(Exception, tries=6, delay=3, backoff=2)
        def _get_image(session, url, data={}, proxies=None, headers=None):
            response = session.post(url, data=data, proxies=proxies,
                                    headers=headers)
            mark_img_xml = response.content
            mark_img_dom = md.parseString(mark_img_xml)

            if not len(mark_img_dom.getElementsByTagName('ObjectFormat')):
                self.logger.error('FAIL TO DOWNLOAD IMG %s' % url)
                return None, None
            mark_img_ext = mark_img_dom.getElementsByTagName(
                'ObjectFormat')[0].firstChild.nodeValue.lower()
            mark_img_dat = mark_img_dom.getElementsByTagName(
                'ObjectData')[0].firstChild.nodeValue
            return mark_img_ext, mark_img_dat

        return _get_image(session, self.api_image_url, data=post_data,
                          proxies=self.proxy_params, headers=self.headers_img)

    def collect_files(self, input_xml):
        ns = 'http://www.iponz.govt.nz/XMLSchema/trademarks/information'
        ET.register_namespace('', ns)
        appnum_list = []
        context = ET.iterparse(input_xml, events=('end', ))
        for event, elem in context:
            if elem.tag[0] == "{":
                uri, tag = elem.tag[1:].split("}")
            else:
                tag = elem.tag
            # should not get to this as the download step
            # will not output a file with transaction error
            if tag == 'TransactionError':
                raise Exception(
                    '%s has a transaction errror. abort!' % input_xml)

            if tag == 'TradeMark':
                appnum = elem.find(
                    '{%(ns)s}ApplicationNumber' % {'ns': ns}).text
                appnum_list.append(appnum)

        # for every application number, get its details into an xml file
        with requests.session() as session:
            for appnum in appnum_list:
                sub_output = {}

                # saving xml files
                appxml_file = os.path.join(self.extraction_dir, 'xml', '%s.xml' % appnum)
                if os.path.exists(appxml_file):
                    self.add_xml_file(appnum, appxml_file)

                    appimgs = glob.glob(os.path.join(self.extraction_dir, 'img',
                                                     '%s.*' % (appnum)))
                    for appimg in appimgs:
                        self.add_img_file(appnum, appimg)
                    continue

                self.logger.info('appnum %s' % appnum)

                mark_dom = self.get_application(session, appnum)
                if mark_dom is None:
                    continue
                save_xml(mark_dom, appxml_file, addindent='  ', newl='\n')

                sub_output['appnum'] = appnum
                self.add_xml_file(appnum, appxml_file)

                # see if there is an image and get it
                mark_imgs = mark_dom.getElementsByTagName(
                    'MarkImageFilename')
                if not len(mark_imgs):
                    continue

                sub_output['img'] = []

                # saving img files
                for idx, mark_img in enumerate(mark_imgs):
                    mark_img_val = str(mark_img.firstChild.nodeValue)
                    post_data = '<soapenv:Envelope xmlns:get="http://' \
                                'data.business.govt.nz/services/' \
                                'getDocument" xmlns:soapenv="http://' \
                                'schemas.xmlsoap.org/soap/envelope/">' \
                                '<soapenv:Body><get:getDocument>' \
                                '<get:ObjectIdentifier>%s' \
                                '</get:ObjectIdentifier>' \
                                '</get:getDocument></soapenv:Body>' \
                                '</soapenv:Envelope>'
                    post_data = post_data % mark_img_val

                    mark_img_ext, mark_img_dat = self.get_image(
                        session, post_data)
                    mark_img_dest = os.path.join(
                        self.extraction_dir, 'img', '%s.%d.%s' % (
                            appnum, idx + 1, mark_img_ext))
                    with open(mark_img_dest, 'wb') as fh:
                        fh.write(base64.b64decode(mark_img_dat))
                    self.add_img_file(appnum, mark_img_dest)
        os.remove(input_xml)

    def process(self):
        pass