import os
import re
import codecs
import dicttoxml
import xml.dom.minidom as md
from pypers.utils.xmldom import save_xml
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract MATM archive
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
                    "name": "img_ref_dir",
                    "descr": "the directory that contains previous extractions,"
                             " for looking at images that are referenced in the"
                             " mark files but not present in the archive"""
                }
            ]
        }
    }

    def collect_files(self, dest):
        self.img_map = {}
        marks_file = None
        for r, d, files in os.walk(dest):
            for dir in d:
                if dir == 'image' or dir == 'images':
                    for img_f in os.listdir(os.path.join(r, dir)):
                        image_name = os.path.splitext(img_f)[0]
                        self.img_map[image_name] = os.path.join(r, dir, img_f)
            for f in files:
                if f.endswith('.txt'):
                    marks_file = os.path.join(r, f)
                    break
        self._proces_mark(marks_file)

    def _fix_file(self, file, img_map):
        """iso-8859-1 charset and windows carriage returns"""
        records = []  # to hold multiline record list
        record = []
        inid_re = re.compile(r'^\((?P<inid>\d{3})\)\s*(?P<val>.*)$')
        gs_re = re.compile(r'^(?P<nb>\d{1,2})\s*(?P<desc>.*)$')
        ap_re = re.compile(r'^(?P<country>[A-Z]{2,3})?\s*:\s*'
                           r'(?P<name>[^@]*)\s*@\s*(?P<address>[^@]*)@?$')

        code_value_mapper = {
            '116': 'RegistrationNumber', '210': 'ApplicationNumber',
            '220': 'ApplicationDate', '180': 'ExpiryDate',
            '190': 'RegistrationOfficeCode', '117': 'PreviousRegistrationNumber',
            '441': 'PublicationDate', '540': 'MarkVerbalElementText',
            '550': 'MarkFeature', '551': 'RegistrationDate',
        }
        # clean file from empty lines and spaces
        with codecs.open(file, 'rb', 'iso-8859-1') as inf:
            for line in inf:
                # remove embedded line breaks
                line = line.replace(
                    '\r', '').replace('\n', ' ').rstrip().lstrip()

                # empty line - move on
                if not line:
                    continue

                match = re.search(inid_re, line)
                if match:
                    inid = match.group('inid')
                    if inid == '111':
                        if len(record):
                            records.append(record)
                        record = []
                    record.append(line)
                else:
                    record.append(line)
        # Stefan added this
        records.append(record)
        marks = []
        mark = {}
        for record in records:
            for idx in range(0, len(record)):
                line = record[idx]
                match = re.search(inid_re, line)

                if match:
                    inid = match.group('inid')
                    value = match.group('val')

                    if inid == '511':
                        mark['GoodsServicesDetails'] = []

                        while True:
                            next_line = record[idx+1]
                            match_nextline_gs = re.search(gs_re, next_line)

                            if not match_nextline_gs:
                                break
                            idx += 1
                            gs_doc = {
                                'ClassNumber':
                                    match_nextline_gs.group('nb'),
                                'GoodsServicesDescription':
                                    match_nextline_gs.group('desc')
                            }
                            mark['GoodsServicesDetails'].append(gs_doc)
                        continue

                    if not value:
                        continue  # nothing to do here

                    if inid == '111':
                        # adding the previous mark
                        if len(mark.keys()) > 0:
                            marks.append(mark)

                        # starting a new mark
                        mark = {}
                        mark_img = img_map.get(value, None)
                        if mark_img:
                            mark['MarkImage'] = mark_img
                    for key, elem in code_value_mapper.items():
                        if inid == key:
                            mark[elem] = value

                    if inid == '591':
                        if 'MarkImage' in mark.keys():
                            mark['MarkImageColourClaimedText'] = value

                    if inid == '300':
                        priorities = list(filter(
                            None, (value or '').split(';')))
                        if len(priorities):
                            mark['PriorityDetails'] = []
                        for priority in priorities:
                            pvalues = re.split(r'\s+', priority)
                            if len(pvalues) < 3:
                                continue  # bad data, ignore
                            pdict = {}
                            pdict['Priority'] = {}
                            pdict['Priority']['CountryCode'] = pvalues[1]
                            pdict['Priority']['PriorityNumber'] = pvalues[2]
                            pdict['Priority']['PriorityDate'] = pvalues[0]
                            mark['PriorityDetails'].append(pdict)

                    if inid == '730':
                        mark['ApplicantDetails'] = []
                        applicants = value.split('@;')
                        for applicant in applicants:
                            match = ap_re.search(applicant)
                            if not match:
                                continue  # bad data, ignore

                            adict = {
                                'Applicant': {
                                    'FullName': match.group('name'),
                                    'AddressCountry':
                                        match.group('country'),
                                    'AddressLine': match.group('address')
                                }
                            }
                            mark['ApplicantDetails'].append(adict)

                    if inid == '740':
                        mark['RepresentativeDetails'] = []
                        rdict = {
                            'Representative': {
                                'FullName': value
                            }
                        }
                        mark['RepresentativeDetails'].append(rdict)

                    if inid == '000':
                        mark['Status'] = value
        return marks

    def _proces_mark(self, marks_file):
        if not marks_file:
            return
        self.logger.info('marks file: %s' % marks_file)
        # extracting marks.txt
        marks = self._fix_file(marks_file, self.img_map)
        xml_dest = os.path.join(self.extraction_dir, 'xml')
        os.makedirs(xml_dest, exist_ok=True)
        for mark in marks:
            appnum = mark.get('ApplicationNumber')
            mark_img = mark.get('MarkImage', None)
            if mark_img:
                self.add_img_file(appnum, mark_img)
            xml_string = dicttoxml.dicttoxml(
                mark, attr_type=False, custom_root='TradeMark',
                item_func=lambda x: x[:-1])
            xml_file = os.path.join(xml_dest, '%s.xml' % appnum)
            save_xml(md.parseString(xml_string), xml_file,
                     addindent='  ', newl='\n')
            self.add_xml_file(appnum, xml_file)
        os.remove(marks_file)

    def process(self):
        pass