import os
import glob
from xml.dom.minidom import parse
from pypers.utils import xmldom
from pypers.steps.base.extract_step import ExtractStep
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract ESTM archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def process(self):
        pass

    def add_xml_file(self, filename, fullpath):
        if 'DATA-' not in filename:
            return
        data_dom = parse(fullpath)
        appnum = xmldom.get_nodevalue('ApplicationNumber', dom=data_dom)

        if not appnum:
            self.logger.info('extract %s does not have an'
                             ' ApplicationNumber' % filename)
            return
        sub_folder = os.path.dirname(fullpath)
        # not really necessary here, but just in case
        appnum = appnum.replace('/', '').replace('-', '')

        # rename to appnum.xml
        xml_data_rename = os.path.join(self.extraction_dir, '%s.xml' % appnum)
        os.rename(fullpath, xml_data_rename)
        fullpath = xml_data_rename
        files_mapper = ['Applicant', 'Representative']
        for type in files_mapper:
            xml_files = glob.glob(
                os.path.join(sub_folder,'%s-*.xml' % type.upper()))
            data_node = data_dom.getElementsByTagNameNS(
                '*', '%sDetails' % type)
            for xml_file in xml_files:
                app_dom = parse(xml_file)
                app_node = app_dom.getElementsByTagNameNS(
                    '*', type)
                if len(app_node) and len(data_node):
                    data_node[0].appendChild(app_node[0])
                os.remove(xml_file)
        xmldom.save_xml(data_dom, fullpath)
        self.manifest['data_files'].setdefault(appnum, {})
        self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
            fullpath, self.extraction_dir
        )

        img_uri = xmldom.get_nodevalue('MarkImageURI', dom=data_dom)
        self.logger.info('%s - %s' % (appnum, img_uri))
        if img_uri:
            img_uri = 'http://consultas2.oepm.es/WSLocalizador/' \
                      'GeneracionImagenServlet?numeroMarca=%s' % appnum
            self.add_img_url(appnum, img_uri)
