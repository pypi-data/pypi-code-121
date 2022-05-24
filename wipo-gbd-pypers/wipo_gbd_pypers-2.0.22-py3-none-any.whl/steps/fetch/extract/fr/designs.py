import os
import math
import shutil
import glob
import codecs
import xml.etree.ElementTree as ET
from pypers.utils import utils
from pypers.steps.base.extract_step import ExtractStep


class Designs(ExtractStep):
    """
    Extract FRID_XML archive
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
                             " for looking at images that are referenced in "
                             "the xml files but not present in the archive"
                }
            ],
            "outputs": [
                {
                    "name": "del_list",
                    "descr": "del file that contains a list of application "
                             "numbers to be deleted"
                },
            ]
        }
    }

    def _get_sub_folder(self, _):
        return 'dest'

    def get_raw_data(self):
        self.get_xmls_files_with_xml_and_img_path()
        if len(self.input_archive) == 0:
            return [], {}
        new_files = glob.glob(os.path.join(self.dest_dir[0], 'FR_FRNEW*.xml'))
        amd_files = glob.glob(os.path.join(self.dest_dir[0], 'FR_FRAMD*.xml'))
        del_files = glob.glob(os.path.join(self.dest_dir[0], 'FR_FRDEL*.xml'))

        xml_files = []
        xml_files.extend(new_files)
        xml_files.extend(amd_files)
        xml_files.extend(del_files)
        img_map = {}
        for root, dirs, files in os.walk(self.img_dest_dir[0]):
            self.common_walker(root, dirs, files, xml_files, img_map)
        return xml_files, img_map

    def _image_ref_handle(self, img_name, appnum, design_ref, img_nb,
                          img_count, sub_output, extraction_data, img_dest,
                          img_map=None, appuid=None, upd_mode=None):
        from_ref = False
        img_file = img_map.get(img_name)

        if img_file is None:
            img_folder = utils.appnum_to_dirs(
                self.img_ref_dir, appnum)
            found_high = glob.glob(os.path.join(
                img_folder,
                '%s-%s.%s.high.*' % (appnum,
                                     design_ref.zfill(4),
                                     img_nb)))
            self.logger.info(os.path.join(
                img_folder,
                '%s-%s.%s.high.*' % (appnum,
                                     design_ref.zfill(4),
                                     img_nb)))
            if len(found_high) > 0:
                img_file = found_high[0]
                from_ref = True

        if img_file is None:
            self.logger.info('[%s] %s - img missing - %s' % (
                upd_mode, appuid, img_name))
            extraction_data.append(sub_output)
            return img_count
        self.logger.info('[%s] %s - %s' % (
            upd_mode, appuid, '%s.%s' % (appuid, img_nb)))
        img_count += 1
        img_ext = os.path.splitext(img_file)[1]
        img_dest_name = '%s.%s%s' % (appuid, img_nb,
                                     img_ext)
        img_dest_file = os.path.join(img_dest,
                                     img_dest_name)

        # copy image if from ref_dir
        if from_ref:
            shutil.copyfile(img_file, img_dest_file)
        # move image if from extraction dir
        else:
            os.rename(img_file, img_dest_file)
        sub_output['img'].append(
            os.path.relpath(img_dest_file, self.dest_dir[0]))
        return img_count

    def process_xml_data(self, data):
        extraction_data = []
        del_list = []
        xml_files = data[0]
        img_map = data[1]
        ns = 'http://www.wipo.int/standards/XMLSchema/designs'
        ET.register_namespace('', ns)
        xml_count = img_count = 0
        for xml_file in xml_files:
            upd_mode = os.path.basename(xml_file)
            upd_mode = upd_mode[5:8]
            self.logger.info('\nprocessing file: %s' % xml_file)
            context = ET.iterparse(xml_file, events=('end', ))
            for event, elem in context:
                if elem.tag[0] == "{":
                    uri, tag = elem.tag[1:].split("}")
                else:
                    tag = elem.tag
                if tag == 'DesignApplication':
                    xml_count += 1
                    sub_output = {}

                    appnum = elem.find(
                        '{%(ns)s}DesignApplicationNumber' % {'ns': ns}).text
                    dsnnum = elem.find(
                        '{%(ns)s}DesignDetails/{%(ns)s}Design/'
                        '{%(ns)s}DesignReference' % {'ns': ns}).text
                    appuid = '%s-%s' % (appnum, dsnnum.zfill(4))

                    if upd_mode == 'DEL':
                        del_list.append({
                            'id': 'FRID.%s' % appuid,
                            'fname': appuid,
                            'fdir': utils.appnum_to_subdirs(appnum)})
                        self.logger.info('[DEL] %s' % appuid)
                        continue

                    # 100 in a dir
                    subdir = str(int(math.ceil(xml_count/100 + 1))).zfill(4)

                    xml_dest = os.path.join(self.subfolders['xml'], subdir)
                    img_dest = os.path.join(self.subfolders['img'], subdir)

                    if not os.path.exists(xml_dest):
                        os.makedirs(xml_dest)
                    if not os.path.exists(img_dest):
                        os.makedirs(img_dest)

                    appxml_file = os.path.join(
                        xml_dest, '%s-%s.xml' % (appnum, dsnnum.zfill(4)))
                    with codecs.open(appxml_file, 'w', 'utf-8') as fh:
                        fh.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                        fh.write(ET.tostring(elem).decode("utf-8"))
                    sub_output['appnum'] = appnum
                    sub_output['xml'] = os.path.relpath(appxml_file,
                                                        self.dest_dir[0])
                    sub_output['img'] = []
                    design_elems = elem.findall(
                        '{%(ns)s}DesignDetails/{%(ns)s}Design' % {'ns': ns})
                    for design_elem in design_elems:
                        design_ref = design_elem.find(
                            '{%(ns)s}DesignReference' % {'ns': ns}).text
                        view_elems = design_elem.findall(
                            '{%(ns)s}DesignRepresentationSheetDetails/'
                            '{%(ns)s}DesignRepresentationSheet/'
                            '{%(ns)s}ViewDetails/'
                            '{%(ns)s}View' % {'ns': ns})
                        for view_elem in view_elems:
                            img_nb = view_elem.find(
                                '{%(ns)s}ViewSequenceNumber' % {'ns': ns}).text
                            try:
                                img_name = view_elem.find(
                                    '{%(ns)s}ViewNumber' % {'ns': ns}).text
                            except Exception as e:
                                self.logger.info('[%s] %s - img tag missing' % (
                                    upd_mode, appuid))
                                extraction_data.append(sub_output)
                                continue

                            if img_name is None:
                                continue
                            img_count = self._image_ref_handle(
                                img_name, appnum, design_ref, img_nb,
                                img_count, sub_output, extraction_data,
                                img_dest, img_map=img_map, appuid=appuid,
                                upd_mode=upd_mode)
                    extraction_data.append(sub_output)
            os.remove(xml_file)
        self.output_data = [extraction_data]
        return xml_count, img_count
