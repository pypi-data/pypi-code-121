import os
import mimetypes
from pypers.steps.base.extract_step import ExtractStep
from pypers.utils import xmldom


class Designs(ExtractStep):
    """
    Extract CAID archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def _walker(self, r, d, files, xml_files, img_map):
        # skip application images -- not necessary

        for file in files:
            # ignore files under applications folder
            # (photographs of application documents)
            if os.path.basename(r) == 'applications':
                os.remove(os.path.join(self.dest_dir[0], r, file))
                continue

            if file.lower().endswith('.xml'):
                rdir = os.path.relpath(r, self.dest_dir[0])
                xml_files.append(os.path.join(rdir, file))
            else:
                file_mime = mimetypes.guess_type(file)[0]
                if (file_mime or '').startswith('image/'):
                    fname = os.path.basename(file)
                    fname = fname[0:fname.rfind('-')].lower()
                    rdir = os.path.relpath(r, self.dest_dir[0])
                    img_map.setdefault(fname, [])
                    img_map[fname].append(os.path.join(rdir, file))

    def get_raw_data(self):
        return self.get_xmls_files_with_path(self._walker)

    def process_xml_data(self, data):
        extraction_data = []
        xml_files = data[0]
        img_map = data[1]
        img_count = 0
        for fxml in xml_files:
            xmldom.clean_xmlfile(os.path.join(self.dest_dir[0], fxml),
                                 overwrite=True)
            appnum = xmldom.get_nodevalue(
                'DesignApplicationNumber', file=os.path.join(
                    self.dest_dir[0],fxml),
                ns='http://www.wipo.int/standards/XMLSchema/designs')
            if not appnum:
                self.bad_files.append(fxml)
                continue

            sub_output = {}
            sub_output['appnum'] = appnum.replace('-', '')  # 7-Z -> 7Z
            sub_output['xml'] = fxml
            sub_output['img'] = []

            imgs = img_map.get(appnum.lower(), [])

            # rename image to 123-0001.1, 123-0001.2, ...
            img_idx = 0
            for img in sorted(imgs):
                img_idx += 1

                _, img_ext = os.path.splitext(img)
                img_path = os.path.dirname(img)
                img_name = '%s-%s.%d%s' % (
                    appnum.replace('-', ''), '0001', img_idx, img_ext)
                os.rename(os.path.join(self.dest_dir[0], img),
                          os.path.join(self.dest_dir[0], img_path, img_name))
                sub_output['img'].append(
                    os.path.join(img_path, img_name))
                self.logger.info("%s %s" % (appnum, img))

            img_count += img_idx
            extraction_data.append(sub_output)

        self.output_data = [extraction_data]
        return len(xml_files), img_count
