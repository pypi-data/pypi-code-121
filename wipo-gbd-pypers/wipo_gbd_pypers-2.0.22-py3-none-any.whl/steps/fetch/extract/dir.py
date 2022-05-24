import os
import glob
from pypers.utils.xmldom import clean_xmlfile
from pypers.steps.base.extract_step import ExtractStep


class Dir(ExtractStep):
    """
    Extract DKTM archives
    """
    spec = {
        "version": "0.1",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "sdir",
                    "type": "dir",
                    "descr": "the archives to extract"
                }
            ],
        }
    }

    def process(self):

        self.archive_name = 'hack'
        extraction_data = []
        dest_dir = self.sdir
        xml_files = glob.glob(os.path.join(self.sdir, '*.xml'))
        img_files = glob.glob(os.path.join(self.sdir, '*.jpg'))
        img_map = {}
        for f in img_files:
            appnum = os.path.basename(f)
            appnum = appnum[0:appnum.index('.')]
            img_map[appnum] = f
        for f in xml_files:
            f = clean_xmlfile(f, overwrite=True)

            appnum = os.path.splitext(os.path.basename(f))[0]
            sub_output = {}
            sub_output['appnum'] = appnum
            sub_output['xml'] = f

            if appnum in img_map.keys():
                sub_output['img'] = img_map[appnum]

            extraction_data.append(sub_output)

        self.output_data = [extraction_data]
        self.dest_dir = [dest_dir]
