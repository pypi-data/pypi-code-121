import os
import mimetypes
from xml.dom.minidom import parse
from pypers.utils import xmldom
from pypers.steps.base.extract_step import ExtractStep


class Designs(ExtractStep):
    """
    Extract CNID archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def _walker(self, r, d, files, xml_files, img_files):
        # skip application images -- not necessary

        for file in files:
            name, ext = os.path.splitext(file)
            path = os.path.join(r, file)
            parent = os.path.basename(r)
            if ext.lower() == '.xml':
                xml_files.append(path)
            else:  # not an xml, then most probably image
                file_mime = mimetypes.guess_type(file)[0]
                if (file_mime or '').startswith('image/'):
                    img_files.setdefault(parent, [])
                    img_files[parent].append(path)

    def get_raw_data(self):
        return self.get_xmls_files_with_path(self._walker)

    def process_xml_data(self, data):
        extraction_data = []
        xml_files = data[0]
        img_files = data[1]
        img_count = 0
        for xml_file in xml_files:
            fname = os.path.splitext(os.path.basename(xml_file))[0]

            xml_dom = parse(xml_file)

            appnum = xmldom.get_nodevalue('PatentNumber', dom=xml_dom)

            # sometimes files do not have any bibliographical data!
            if not appnum:
                self.logger.error('!! ERROR: %s file is incomplete' % xml_file)
                continue

            appnum = appnum[2:]  # remove the leading CN
            # remove the trailing .X if any
            try:
                appnum = appnum[0:appnum.index('.')]
            except Exception as e:
                pass
            # get rid of the dtd declaration
            xml_dest_file = os.path.join(self.dest_dir[0], '%s.xml' % appnum)
            with open(xml_dest_file, 'wb') as fh:
                fh.write(b"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                fh.write(xml_dom.childNodes[1].toxml(encoding='utf-8'))
            os.remove(xml_file)
            xml_dom.unlink()

            # append the 0001 to be used in renaming the images
            sub_output = {}
            sub_output['appnum'] = '%s-0001' % appnum
            sub_output['xml'] = os.path.relpath(xml_dest_file,
                                                self.dest_dir[0])
            sub_output['img'] = []

            self.logger.info(appnum)
            for img in sorted(img_files.get(fname, [])):
                sub_output['img'].append(os.path.relpath(img, self.dest_dir[0]))
                img_count += 1
                self.logger.info('  - %s' % (os.path.basename(img)))

            extraction_data.append(sub_output)

        self.output_data = [extraction_data]
        return len(xml_files), img_count
