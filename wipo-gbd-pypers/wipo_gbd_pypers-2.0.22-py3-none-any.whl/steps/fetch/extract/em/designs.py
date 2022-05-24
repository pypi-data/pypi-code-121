import os
import glob
import shutil
import codecs
import mimetypes
import xml.etree.ElementTree as ET
from pypers.utils import utils
from pypers.steps.base.extract_step import ExtractStep


class Designs(ExtractStep):
    """
    Extract EMID_XML archive
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
                    "name": "img_dest_dir",
                    "descr": "the directory that contains image extractions"
                },
                {
                    "name": "img_ref_dir",
                    "descr": "the directory that contains previous extractions,"
                             " for looking at images that are referenced in the"
                             " xml files but not present in the archive"
                }
            ],
            "outputs": [
                {
                    "name": "del_list",
                    "descr": "del file that contains a list of application"
                             " numbers to be deleted"
                },
            ],
        }
    }

    def _get_sub_folder(self, _):
        return 'dest'

    def get_raw_data(self):
        self.get_xmls_files_with_xml_and_img_path()
        xml_files = []
        # extraction path not always consistent => walk the tree
        for root, dirs, files in os.walk(self.dest_dir[0]):
            self.common_walker(root, dirs, files, xml_files, {})

        img_files = {}  # key=filename value=filepath
        # extraction path not always consistent => walk the tree
        for root, dirs, files in os.walk(self.img_dest_dir[0]):
            for file in files:
                name, ext = os.path.splitext(file)
                name = name[name.rfind('\\') + 1:]
                num = name[0:name.rfind('_')].replace('_', '-')
                path = os.path.join(root, file)
                file_mime = mimetypes.guess_type(file)[0]
                if (file_mime or '').startswith('image/'):
                    img_files.setdefault(num, [])
                    img_files[num].append(path)
        return xml_files, img_files

    def process_xml_data(self, data):
        extraction_data = []
        self.del_list = []
        xml_files = data[0]
        img_files = data[1]
        xml_count = img_count = 0
        ns = 'http://euipo.europa.eu/design/data'
        ET.register_namespace('', ns)

        for xml_file in xml_files:
            context = ET.iterparse(xml_file, events=('end', ))
            for event, elem in context:
                if elem.tag[0] == "{":
                    uri, tag = elem.tag[1:].split("}")
                else:
                    tag = elem.tag

                if tag == 'Design':
                    sub_output = {}

                    dsgnum = elem.find(
                        '{%(ns)s}DesignIdentifier' % {'ns': ns}).text
                    appnum = dsgnum[0:dsgnum.index('-')]
                    upd_mode = elem.attrib['operationCode']

                    if upd_mode == 'Delete':
                        self.del_list.append({
                            'id': 'EMID.%s' % dsgnum,
                            'fname': dsgnum,
                            'fdir': utils.appnum_to_subdirs(appnum)})
                    # only write the Design element
                    appxml_file = os.path.join(self.subfolders['xml'],
                                               '%s.xml' % (dsgnum))
                    with codecs.open(appxml_file, 'w', 'utf-8') as fh:
                        fh.write(ET.tostring(elem, 'utf-8').decode("utf-8"))

                    sub_output['appnum'] = dsgnum
                    sub_output['xml'] = os.path.relpath(appxml_file,
                                                        self.dest_dir[0])
                    xml_count += 1
                    sub_output['img'] = []
                    self.logger.info('%s: %s' % (dsgnum, upd_mode.lower()))
                    if not upd_mode.lower() == 'delete':
                        from_ref = False
                        # get imgs from ref directory

                        img_folder = utils.appnum_to_dirs(
                            self.img_ref_dir, appnum)
                        imgs_ref = glob.glob(os.path.join(
                            img_folder,
                            '%s.*.high.*' % (dsgnum)
                        ))
                        # priority to images found in the update archive
                        imgs = img_files.pop(dsgnum, None)
                        if not imgs:
                            from_ref = True
                            imgs = imgs_ref

                        for idx, img_file in enumerate(sorted(imgs)):
                            self.logger.info('  %s: %s from ref: %s' % (
                                idx+1, img_file, from_ref))

                            # the image has been processed in a parallel
                            # extraction. good enough !
                            if not os.path.exists(img_file):
                                continue
                            img_count += 1
                            _, img_ext = os.path.splitext(img_file)
                            img_dest_name = '%s.%s%s' % (
                                dsgnum, idx+1, img_ext)
                            img_dest_file = os.path.join(
                                self.subfolders['img'], img_dest_name)

                            if from_ref:
                                shutil.copyfile(img_file, img_dest_file)
                            else:
                                os.rename(img_file, img_dest_file)
                            sub_output['img'].append(
                                os.path.relpath(img_dest_file, self.dest_dir[0]))
                    extraction_data.append(sub_output)
                    elem.clear()
            # remove original xml file
            os.remove(xml_file)
        self.output_data = [extraction_data]
        return xml_count, img_count
