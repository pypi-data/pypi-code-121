import os
import requests
import xml.dom.minidom as md
from distutils.dir_util import remove_tree
from pypers.utils import xmldom
from pypers.utils import utils
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract DKTM archives
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
        # Prepare AP and RP
        for key in ['AP', 'RE']:
            for archive in archives:
                if key in os.path.basename(archive):
                    dest = self.unpack_archive(archive, os.path.join(self.extraction_dir, key))
                    for f in os.listdir(dest):
                        xml_file = os.path.join(dest, f)
                        applicant_nb = os.path.splitext(
                            os.path.basename(xml_file))[0]
                        self.xml_data_map[key][applicant_nb] = xml_file
        for archive in archives:
            if 'TM' in os.path.basename(archive):
                break
        # unpack the archives and collect the files
        self.collect_files(self.unpack_archive(archive, self.extraction_dir))

    def process(self):
        for xml_type in self.xml_data_map.keys():
            try:
                remove_tree(os.path.join(self.manifest['extraction_dir'], xml_type))
            except Exception as e:
                pass


    def add_xml_file(self, filename, fullpath):
        proxy_params = self.get_connection_params()
        xml_tag_mapping = {'AP': 'Applicant', 'RE':  'Representative'}
        # open a session to download missing applicants and representatives
        with requests.session() as session:
            # happens that the data file is empty :(
            try:
                xmldom.clean_xmlfile(fullpath, overwrite=True)
            except:
                self.logger.info('[%s] bypassing' % filename)
                return
            data_dom = md.parse(fullpath)
            appnum = xmldom.get_nodevalue('ApplicationNumber',
                                          dom=data_dom)
            if not appnum:
                self.logger.info(
                    'file %s does not have an ApplicationNumber' %
                    filename)
                return
            appnum = appnum.replace(' ', '')
            for xml_type in xml_tag_mapping.keys():
                data_node = data_dom.getElementsByTagName(
                    '%sKey' % xml_tag_mapping[xml_type])
                for node in data_node:
                    uri = xmldom.get_nodevalue(
                        'URI', dom=node)
                    nb = os.path.basename(uri)
                    dfile = self.xml_data_map[xml_type].get(nb, None)
                    # found in the update archive
                    if dfile:
                        dom = md.parse(xmldom.clean_xmlfile(
                            dfile, overwrite=False))
                        self.logger.info('%s %s - in update archive' % (
                            xml_type, nb))
                    # not found, download it
                    else:
                        self.logger.info('%s %s - %s' % (
                            xml_type, nb, uri))
                        response = session.get(uri, proxies=proxy_params)
                        dom = md.parseString(response.content)
                    tnode = dom.getElementsByTagName(
                        xml_tag_mapping[xml_type])
                    if len(tnode):
                        node.appendChild(tnode[0])
                    # rename to appnum.xml
            xml_data_rename = os.path.join(os.path.dirname(fullpath), '%s.xml' % appnum)
            xmldom.save_xml(
                data_dom, xml_data_rename, newl='\n', addindent='  ')
            img_uri = xmldom.get_nodevalue('MarkImageURI', dom=data_dom)

            os.remove(fullpath)
            self.manifest['data_files'].setdefault(appnum, {})
            self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                xml_data_rename, self.extraction_dir
            )
            if img_uri:
                self.add_img_url(appnum, img_uri)
