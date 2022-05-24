import os
from pypers.steps.fetch.extract.fr.designs import Designs


class DesignsGlobal(Designs):
    """
    Extract FRID_XML archive
    """
    def get_raw_data(self):
        self.get_xmls_files_with_xml_and_img_path()
        xml_files = os.listdir(self.dest_dir[0])
        xml_files = [os.path.join(self.dest_dir[0], f)
                     for f in xml_files if f.endswith('.xml')]
        return xml_files, {}

    def _image_ref_handle(self, img_name, appnum, design_ref, img_nb,
                          img_count, sub_output, extraction_data, img_dest,
                          img_map=None, appuid=None, upd_mode=None):
        img_name = img_name.replace('dmf000', 'dmf')

        fname = img_name[0:img_name.find('_')].replace(
            'dmf', '').replace('bis', '').lstrip('0')
        # 905869 -> ['000', '000', '000', '905', '869']
        img_path_parts = [fname.zfill(15)[i:i + 3]
                          for i in range(0, 15, 3)]
        img_sdir = os.path.join(self.img_dest_dir[0],
                                *img_path_parts)

        img_files = os.listdir(img_sdir) \
            if os.path.exists(img_sdir) else []
        self.logger.info(img_sdir)

        if not len(img_files):
            self.logger.error("%s %s %s %s %s -- ERROR - no img" % (
                appnum, design_ref, img_nb, img_name, img_sdir))

        for img_file in img_files:
            self.logger.info("%s %s %s %s %s" % (
                appnum, design_ref, img_nb, img_name, img_sdir))
            img_ext = os.path.splitext(img_file)[1]
            img_dest_name = '%s-%s.%s%s' % (
                appnum, design_ref.zfill(4),
                img_nb, img_ext)
            img_dest_file = os.path.join(
                img_dest, img_dest_name)
            img_file = os.path.join(img_sdir, img_file)

            os.rename(img_file, img_dest_file)
            img_count += 1
            sub_output['img'].append(
                os.path.relpath(img_dest_file, self.dest_dir[0]))
        return img_count
