import os
import mimetypes
import xml.dom.minidom as md
from pypers.utils.xmldom import save_xml
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract MDTM archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "outputs": [
                {
                    "name": "del_list",
                    "descr": "del file that contains a list of application"
                             " numbers to be deleted"
                }
            ],
        }
    }

    def file_in_archive(self, file, path):
        f_name, ext = os.path.splitext(os.path.basename(file))
        if ext.lower() == '.xml':
            # f_nmae is appnum
            self.add_xml_file(f_name, os.path.join(path, file))
        else:
            file_mime = mimetypes.guess_type(file)[0]
            if (file_mime or '').startswith('image/'):
                self.img_files[f_name] = os.path.join(path, file)

    def add_xml_file(self, filename, fullpath):
        xml_dir = os.path.join(self.extraction_dir, 'xml')
        if not os.path.exists(xml_dir):
            os.makedirs(xml_dir)

        xml_dom = md.parse(fullpath)
        trdmrks = xml_dom.getElementsByTagName('TradeMark')

        # reversed to get newer updates first
        # sometimes same trademark is included twice
        # get the last one
        for mark in reversed(trdmrks):
            appnum_tag = mark.getElementsByTagName('ApplicationNumber')[0]
            if not appnum_tag or not appnum_tag.firstChild:
                self.logger.info('%s Empty ApplicationNumber' % mark)
                continue
            appnum = mark.getElementsByTagName(
                'ApplicationNumber')[0].firstChild.nodeValue
            appxml = md.Document()
            # appxml = xml_tmpl.cloneNode(deep=True)
            appxml.appendChild(mark)
            appxml_file = os.path.join(xml_dir, '%s.xml' % appnum)
            save_xml(appxml, appxml_file, addindent='  ', newl='\n')

            self.manifest['data_files'].setdefault(appnum, {})
            self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                appxml_file, self.extraction_dir
            )
            img_tag = mark.getElementsByTagName('MarkImageFilename')
            if len(img_tag):
                img_val = img_tag[0].firstChild.nodeValue
                if img_val:
                    img_name = os.path.basename(img_val)
                    img_name = img_name[0:img_name.index('.')]
                    img_file = self.img_files.get(img_name)
                    if img_file:
                        self.add_img_file(appnum, img_file)
        os.remove(fullpath)

    def process(self):
        pass