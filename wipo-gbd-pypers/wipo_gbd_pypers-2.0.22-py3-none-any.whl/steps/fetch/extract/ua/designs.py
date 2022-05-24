import os
import math
import codecs
import dicttoxml
from xml.dom.minidom import parseString
from pypers.steps.fetch.extract.ua.trademarks import Trademarks


class Designs(Trademarks):
    """
    Extract UAID marks information from api
    """

    def _parse_raw(self, raw, conn_params, count, xml_dir, dest_dir,
                   extraction_data):
        appnum = raw['app_number']

        # sanitize appnum : 97314/SU -> 97314SU
        appnum = appnum.replace('/', '')
        current_img_path = None
        for idx, el in enumerate((raw.get('data', {}) or {}).get("DesignSpecimenDetails", [])):
            dsgnum = str(idx + 1).zfill(5)
            fullnum = "%s-%s" % (appnum, dsgnum)

            sub_dir = str(int(math.ceil(count / 10000 + 1))).zfill(4)
            dest_sub_dir = os.path.join(xml_dir, sub_dir)
            if not os.path.exists(dest_sub_dir):
                os.makedirs(dest_sub_dir)
            mark_file = os.path.join(dest_sub_dir, '%s.xml' % fullnum)
            mark = raw
            mark['app_number'] = fullnum
            mark_xml = dicttoxml.dicttoxml(
                mark, attr_type=False, custom_root='mark')

            # with open(mark_file, 'w') as fh:
            with codecs.open(mark_file, 'w', 'utf-8') as fh:
                fh.write(parseString(mark_xml).toprettyxml())

            sub_output = {}
            sub_output['appnum'] = fullnum
            sub_output['xml'] = os.path.relpath(
                mark_file, dest_dir).replace('.json', '.xml')
            if len(el['DesignSpecimen']):
                sub_output['img_uri'] = []
                for img in el['DesignSpecimen']:
                    if current_img_path is None and os.path.dirname(
                            img['SpecimenFilename']) != '':
                        current_img_path = os.path.dirname(
                            img['SpecimenFilename'])
                    # Second specimen has only the filename
                    if os.path.dirname(img['SpecimenFilename']) == "":
                        img['SpecimenFilename'] = os.path.join(
                            current_img_path, img['SpecimenFilename'])
                    img_uri = "%s%s" % (conn_params['url'],
                                        img['SpecimenFilename'])
                    sub_output['img_uri'].append(img_uri)
            extraction_data.append(sub_output)
            count += 1
        return count
