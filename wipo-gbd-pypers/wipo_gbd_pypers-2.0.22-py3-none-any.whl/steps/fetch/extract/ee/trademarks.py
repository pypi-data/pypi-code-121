import os
import re
import glob
import pandas as pd
import codecs
import dicttoxml
import xml.dom.minidom as md
from pypers.utils import xmldom
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract Trademarks archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def _fix_file(self, file):
        """Cyrillic charset and windows carriage returns
        """
        record_line = re.compile(r'(^[A-Z]*[0-9]+[A-Z]*)\|.*')
        filef = '%s.fix' % file
        records = []
        with codecs.open(file, 'rb', 'cp1252') as inf:
            for line in inf:
                # remove embedded line breaks
                line = line.replace(
                    '\r', '').replace('\n', ' ').rstrip(
                    ' ?').rstrip().lstrip()
                # remove control characters
                line = ''.join(c for c in line if ord(c) >= 32)
                # start of a new record
                match = record_line.match(line)
                if match:
                    records.append([])
                elif not len(line) or line == '|':
                    continue
                if len(records):
                    records[len(records) - 1].append(line)
        if len(records):
            with codecs.open(filef, 'wb', 'utf8') as fixed:
                for record in records:
                    line = ' '.join(record)
                    # every line should end with a '|' character
                    if not line.endswith('|'):
                        line += '|'
                    fixed.write(line + '\n')
            return filef
        else:
            self.logger.info('empty file: %s\n' % file)
            return None

    def _get_mark_details(self, file, header, detail_name,
                          appnum_pattern, marks):
        ffile = self._fix_file(file)
        # sometimes we get empty files
        if not ffile:
            return
        df = pd.read_csv(ffile, sep='|', dtype=str, header=None)
        for mark in df.values:
            appnum = mark[0]

            if not appnum_pattern.match(appnum):
                continue
            if appnum not in marks.keys():
                continue
            marks[appnum].setdefault('%sDetails' % detail_name, [])

            item = {}
            item[detail_name] = {}
            for idx, key in enumerate(header):
                if idx == 0:
                    continue
                if not pd.isnull(mark[idx]):
                    item[detail_name][key] = mark[idx]

            marks[appnum]['%sDetails' % detail_name].append(item)
        os.remove(file)
        os.remove(ffile)

    def collect_files(self, extraction_dir):
        marks_file = os.path.join(extraction_dir, 'mark.txt')
        marks_ffile = self._fix_file(marks_file)
        header = ['appnum', 'ApplicationDate', 'RegistrationNumber',
                  'RegistrationDate', 'ExpiryDate', 'PublicationDate',
                  'MarkVerbalElementText', 'MarkImage',
                  'MarkType', 'EE_Colors', 'Status']

        df = pd.read_csv(marks_ffile, sep='|', dtype=str, header=None)

        appnum_pattern = re.compile("^[A-Z0-9]+$")
        marks = {}
        for mark in df.values:
            appnum = mark[0]
            if not appnum_pattern.match(appnum):
                continue
            marks[appnum] = {}
            marks[appnum]['ApplicationNumber'] = appnum
            for idx, key in enumerate(header):
                if idx == 0:
                    continue
                if not pd.isnull(mark[idx]):
                    marks[appnum][key] = mark[idx]
        files_transformation = {
            # filename: ([headers], detail_name)
            'categpict.txt': (['appnum', 'CategoryCode'], 'CategoryCode'),
            'class.txt': (['appnum', 'ClassNumber', 'GoodsServicesDescription'],
                          'GoodsServices'),
            'priority.txt': (['appnum', 'EE_PriorityNum', 'PriorityDate',
                              'EE_PriorityCountry'], 'Priority'),
            'owner.txt': (['appnum', 'FirstName', 'LastName',
                           'FullName', 'AddressLine', 'AddressPostcode',
                           'AddressCity', 'AddressState', 'AddressCountry'],
                          'Applicant'),
            'representative.txt': (['appnum', 'FirstName', 'LastName',
                                    'OrganizationName','RepAddress',
                                    'AddressPostcode', 'AddressCity',
                                    'AddressCountry'], 'Representative')
        }
        for key, value in files_transformation.items():
            f = os.path.join(extraction_dir, key)
            self._get_mark_details(f, value[0], value[1], appnum_pattern, marks)
        # need to glob here as the imgs folder name is not always consistent !
        imgs_list = glob.glob(os.path.join(extraction_dir, '*', '*'))
        imgs_names = [os.path.splitext(os.path.basename(file))[0]
                      for file in imgs_list]
        # create xml directory
        # ----------------
        xml_dest = os.path.join(extraction_dir, 'xml')
        os.makedirs(xml_dest)

        for appnum, mark in marks.items():
            mark_img = mark.get('MarkImage', None)
            if mark_img:
                try:
                    img_file = imgs_list[
                        imgs_names.index(mark_img)]
                    self.add_img_file(appnum, img_file)
                except Exception as e:
                    mark.pop('MarkImage')

            xml_string = dicttoxml.dicttoxml(
                mark, attr_type=False, custom_root='TradeMark',
                item_func=lambda x: x[:-1])
            xml_file = os.path.join(xml_dest, '%s.xml' % appnum)
            try:
                xmldom.save_xml(md.parseString(xml_string), xml_file,
                                addindent='  ', newl='\n')
                self.add_xml_file(appnum, xml_file)
            except Exception as e:
                with open(xml_file) as fh:
                    fh.write(xml_string)
        # clean
        os.remove(marks_file)
        os.remove(marks_ffile)

    def process(self):
        pass