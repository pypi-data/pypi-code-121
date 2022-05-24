import os
import mimetypes
from pypers.steps.base.extract_step import ExtractStep
import xml.etree.ElementTree as ET
from pypers.utils.xmldom import clean_xmlfile
from pypers.steps.fetch.extract.ipas import get_sub_folders, extract_sub_archive
from pypers.utils import utils


class Designs(ExtractStep):
    """
    Extract IPAS archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "params": [
                {
                    "name": "version",
                    "descr": "the version of the WIPO Publish used",
                    "value": "1.5.0"
                }
            ]
        }
    }

    def get_raw_data(self):
        return get_sub_folders(self)

    def process_xml_data(self, sub_archives):
        extraction_data = []
        ns = 'http://www.wipo.int/standards/XMLSchema/designs'
        ET.register_namespace('', ns)
        xml_count = img_count = 0

        for sub_archive in sub_archives:
            sub_archive_name, sub_dest_dir = extract_sub_archive(
                self, sub_archive)

            # new ipas version has double archiving. hmm
            if self.version == '1.5.1':
                sub_sub_archives = [
                    os.path.join(sub_dest_dir, sub_sub_archive)
                    for sub_sub_archive in os.listdir(sub_dest_dir)
                    if sub_sub_archive.lower().endswith('.zip')]

                for sub_sub_archive in sub_sub_archives:
                    utils.zipextract(sub_sub_archive, sub_dest_dir)
                    os.remove(sub_sub_archive)

            xml_file = None
            img_map = {}  # key=filename value=filepath

            # extraction path not always consistent => walk the tree
            for root, dirs, files in os.walk(sub_dest_dir):
                for file in files:
                    name, ext = os.path.splitext(file)
                    path = os.path.join(root, file)
                    if ext.lower() == '.xml':
                        if name.endswith('_biblio'):
                            xml_file = path
                        else:
                            os.remove(path)
                    else:  # not an xml, then most probably image
                        file_mime = mimetypes.guess_type(file)[0]
                        if (file_mime or '').startswith('image/'):
                            img_map[name.lower()] = path
            if xml_file is None:
                self.logger.error(
                    "No xml found in archive %s" % sub_archive_name)
                self.bad_files.append(self.archive_name[0])
                continue
            xml_count += 1
            img_count += len(img_map.keys())
            xml_file = clean_xmlfile(xml_file, overwrite=True)

            dsnnum = 0  # no DesignReference in xml, use a counter
            context = ET.iterparse(xml_file, events=('end', ))
            for event, elem in context:
                if elem.tag[0] == "{":
                    uri, tag = elem.tag[1:].split("}")
                else:
                    tag = elem.tag

                if tag == 'DesignApplication':
                    dsnnum += 1
                    sub_output = {}

                    try:
                        appnum = elem.find(
                            '{%(ns)s}DesignApplicationNumber' % {'ns': ns}).text
                    except Exception as e:
                        self.bad_files.append(xml_file)
                        continue

                    # sanitize appnum : S/123(8) -> S123-8
                    appnum = appnum.replace(
                        '/', '').replace(
                        '-', '').replace(
                        '(', '-').replace(
                        ')', '')

                    appuid = '%s-%s' % (appnum, str(dsnnum).zfill(4))

                    sub_output['appnum'] = appnum
                    sub_output['xml'] = os.path.relpath(
                        xml_file, self.dest_dir[0])
                    sub_output['img'] = []
                    design_elems = elem.findall(
                        '{%(ns)s}DesignDetails/{%(ns)s}Design' % {'ns': ns})
                    for design_elem in design_elems:
                        view_elems = design_elem.findall(
                            '{%(ns)s}DesignRepresentationSheetDetails/'
                            '{%(ns)s}DesignRepresentationSheet/'
                            '{%(ns)s}RepresentationSheetFilename' % {'ns': ns})

                        for idx, view_elem in enumerate(view_elems):
                            try:
                                img_name, _ = os.path.splitext(view_elem.text)
                            except Exception as e:
                                self.logger.error(
                                    '%s - RepresentationSheetFilename missing' % appuid)
                                extraction_data.append(sub_output)
                                continue
                            img_file = img_map.get(img_name.lower())
                            if img_file is None:
                                self.logger.info('%s - %s - img missing' % (
                                    appuid, img_name))
                                extraction_data.append(sub_output)
                                continue
                            # img found !
                            _, img_ext = os.path.splitext(img_file)
                            img_dest_name = '%s.%s%s' % (appuid,
                                                         (idx+1),
                                                         img_ext)
                            img_dest_file = os.path.join(
                                sub_dest_dir, img_dest_name)

                            os.rename(img_file, img_dest_file)

                            sub_output['img'].append(
                                os.path.relpath(img_dest_file,
                                                self.dest_dir[0]))
                            self.logger.info('%s - %s' % (appuid, img_name))

            extraction_data.append(sub_output)
        if len(sub_archives) != xml_count:
            self.logger.error("There were archives with no xml files")
        self.output_data = [extraction_data]
        return xml_count, img_count
