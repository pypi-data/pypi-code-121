import os
import codecs
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
from pypers.steps.base.extract import ExtractBase


class INN(ExtractBase):
    """
    Extract INN lists
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def save_inn(self, dom, inn_file, code):
        fname = code.replace('/', '-')

        with codecs.open(inn_file, 'wb', 'utf-8') as fh:
            dom_string = md.parseString(
                ET.tostring(dom, 'utf-8')).toprettyxml()
            dom_string = os.linesep.join(
                [s for s in dom_string.splitlines() if s.strip()])
            fh.write(dom_string)
        self.manifest['data_files'].setdefault(fname, {})
        self.manifest['data_files'][fname]['ori'] = os.path.relpath(
            inn_file, self.extraction_dir
        )

    def edit_file(self, inn_file, code, inn, type, list_nb):
        # edit xml document
        dom = ET.parse(inn_file)
        top = dom.getroot()
        # publication type and number and list entry
        elt = ET.SubElement(top, type)
        elt.text = str(list_nb)
        elt.attrib['entry'] = str(inn['list_entry'])
        self.save_inn(top, inn_file, code)

    def new_file(self, inn_file, code, inn, type, list_nb):
        # create the XML Document
        top = ET.Element('inn')
        # code used by WHO
        elt = ET.SubElement(top, 'code')
        elt.text = code
        # publication type and number and list entry
        elt = ET.SubElement(top, type)
        elt.text = str(list_nb)
        elt.attrib['entry'] = str(inn['list_entry'])
        # transliterations
        trans = ET.SubElement(top, 'transliteration')
        for lang in inn['names'].keys():
            elt = ET.SubElement(trans, lang)
            elt.text = inn['names'][lang]
        self.save_inn(top, inn_file, code)

    def extract_type(self, pub_list):
        list_nb = pub_list['number']
        type = pub_list['type'].lower()
        for code, inn in pub_list['publications'].items():
            fname = code.replace('/', '-')
            inn_file = os.path.join(self.extraction_dir, '%s.xml' % fname)
            if os.path.exists(inn_file):
                self.edit_file(inn_file, code, inn, type, list_nb)
            else:
                self.new_file(inn_file, code, inn, type, list_nb)

    def unpack_archive(self, archive, dest):
        return archive

    def collect_files(self, dest):
        with open(dest) as f:
            data = json.loads(f.read())
            for el in data:
                self.extract_type(el)

    def process(self):
        pass


