import os
import mimetypes
import glob
from xml.dom.minidom import parse
from shutil import rmtree
from pypers.utils import utils
from pypers.utils import xmldom
from pypers.steps.base.extract_step import ExtractStep


class Designs(ExtractStep):
    """
    Extract USID archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def get_raw_data(self):
        archive_uid, archive_path, archive_name = self.get_path()
        if archive_uid == None:
            return [], {}
        xml_dir = os.path.join(self.dest_dir[0], 'xml')
        arc_dir = os.path.join(self.dest_dir[0], 'arc')
        os.makedirs(xml_dir)

        self.logger.info('extracting into %s\n' % (arc_dir))

        utils.tarextract(archive_path, arc_dir)
        sub_archives = glob.glob(os.path.join(arc_dir, archive_uid,
                                              'DESIGN', 'USD*.ZIP'))
        self.logger.info('extracted << %s >> sub archives' % len(sub_archives))

        for sub_archive in sub_archives:
            sub_archive_name = os.path.basename(sub_archive)
            sub_dest_dir = os.path.join(
                xml_dir,
                os.path.splitext(sub_archive_name)[0])
            # extract sub archive then delete it
            utils.zipextract(sub_archive, sub_dest_dir)
            os.remove(sub_archive)
        rmtree(arc_dir)

        xml_files = []
        img_map = {}  # key=filename value=filepath
        for root, dirs, files in os.walk(xml_dir):
            for file in files:
                name, ext = os.path.splitext(file)
                path = os.path.join(root, file)
                if ext.lower() == '.xml':
                    xml_files.append(path)
                else:  # not an xml, then most probably image
                    file_mime = mimetypes.guess_type(file)[0]
                    if (file_mime or '').startswith('image/'):
                        name = name[0: name.find('-D')]
                        img_map.setdefault(name, [])
                        img_map[name].append(path)
        return xml_files, img_map

    def process_xml_data(self, data):
        xml_files = data[0]
        img_map = data[1]
        extraction_data = []
        img_count = 0
        for xml_file in xml_files:
            self.logger.info('\nprocessing file: %s' % xml_file)

            fname = os.path.basename(xml_file)
            fname, _ = os.path.splitext(fname)

            xmldom.clean_xmlfile(xml_file, overwrite=True)
            xmldom.remove_doctype(xml_file)
            xml_dom = parse(xml_file)
            appnum = xmldom.get_nodevalue('doc-number', dom=xml_dom)
            xml_dom.unlink()

            if not appnum:
                self.logger.error('!! ERROR: %s file is incomplete' % xml_file)
                continue

            sub_output = {}
            sub_output['appnum'] = '%s-0001' % appnum
            sub_output['xml'] = os.path.relpath(xml_file, self.dest_dir[0])
            sub_output['img'] = []

            imgs = img_map.get(fname, [])
            imgs = utils.sort_human(imgs)
            for img in imgs:
                img_count += 1
                sub_output['img'].append(os.path.relpath(img, self.dest_dir[0]))
                self.logger.info('  - %s' % (os.path.basename(img)))
            extraction_data.append(sub_output)
        self.output_data = [extraction_data]
        return len(xml_files), img_count
