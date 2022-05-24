import os
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract CATM archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "outputs": [
                {
                    "name": "del_list",
                    "descr": "del file that contains a list of "
                             "application numbers to be deleted"
                }
            ]
        }
    }

    to_delete_imgs = []

    def add_img_file(self, appnum, fullpath):
        if os.environ.get('GBD_DEV_EXTRACT_LIMIT', None):
            if len(self.manifest['img_files'].keys()) >= int(
                    os.environ.get('GBD_DEV_EXTRACT_LIMIT')):
                return

        filename = os.path.basename(fullpath)
        _, img_ext = os.path.splitext(filename)

        try:
            appnum = appnum[0:appnum.index('-')]
        except Exception as e:
            rename = '%s-00%s' % (appnum, img_ext)
            dest = fullpath.replace(filename, rename)
            os.rename(fullpath, dest)
            fullpath = dest

        filename = os.path.basename(fullpath)
        new_fullpath = os.path.join(os.path.dirname(fullpath), appnum, filename)
        print(fullpath, '->', new_fullpath)
        os.makedirs(os.path.dirname(new_fullpath), exist_ok=True)
        os.rename(fullpath, new_fullpath)
        path = os.path.relpath(new_fullpath, self.extraction_dir)

        self.manifest['img_files'].setdefault(appnum, [])
        self.manifest['img_files'][appnum].append(
            {'ori': path}
        )

    def add_xml_file(self, appnum, fullpath):
        if os.environ.get('GBD_DEV_EXTRACT_LIMIT', None):
            if len(self.manifest['data_files'].keys()) >= int(
                    os.environ.get('GBD_DEV_EXTRACT_LIMIT')):
                return
        try:
            appnum = appnum[0:appnum.index('-')]
        except Exception as e:
            pass
        """
        # Old delete mechanism 
        del_mode = self.manifest['archive_name'].startswith('CA-TMK-DELETE')
        if del_mode:
            # clean
            os.remove(fullpath)
            self.to_delete_imgs.append(appnum)
            self.logger.info('%s - delete' % appnum)
            return
        """
        self.manifest['data_files'].setdefault(appnum, {})
        self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
            fullpath, self.extraction_dir
        )


    def process(self):
        # Remove images when on del mode
        imgs_keys = self.manifest['img_files'].keys()
        for appnum in self.to_delete_imgs:
            if appnum in imgs_keys:
                for f in self.manifest['img_files'][appnum]:
                    os.remove(f['ori'])
                self.manifest['img_files'].pop(appnum)
