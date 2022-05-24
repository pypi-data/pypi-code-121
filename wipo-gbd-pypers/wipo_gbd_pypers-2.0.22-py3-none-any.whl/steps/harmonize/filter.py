from pypers.steps.base.step_generic import EmptyStep
import json
import os

class Filter(EmptyStep):
    """
    Process manifets file files into subdirectories.
    Rename files and logos to appnum
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
                    "name": "manifest",
                    "descr": "the manifest list",
                    "iterable": True
                }
            ],
            "outputs": [
                {
                    "name": "gbd_extraction_date",
                    "descr": "the data gbd extracted the archive"
                },
                {
                    "name": "extraction_dir",
                    "descr": "the destination dir of the extraction"
                },
                {
                    "name": "data_files",
                    "descr": "the extracted data organized by appnum"
                },
                {
                    "name": "img_files",
                    "descr": "the extracted data organized by appnum"
                },
                {
                    "name": "media_files",
                    "descr": "the extracted data organized by appnum"
                }
            ]
        }
    }

    # self.manifest ORIFILES_DIR/run_id/type/collection/office_extraction_date/archive_name/manifest.json
    def process(self):
        self.extraction_dir = os.path.dirname(self.manifest)

        with open(self.manifest, 'r') as f:
            manifest_data = json.load(f)

        self.gbd_extraction_date = manifest_data['gbd_extraction_date']

        self.data_files = self._filter_missing_files(manifest_data.get('data_files', {}))
        self.img_files  = self._filter_missing_images(manifest_data.get('img_files', {}))

        self.media_files = manifest_data.get('media_files', {})
        

    def postprocess(self):
        self.extraction_dir = [self.extraction_dir]
        self.gbd_extraction_date = [self.gbd_extraction_date]

        self.data_files = [self.data_files]
        self.img_files = [self.img_files]
        self.media_files = [self.media_files]

    def _file_exists(self, file):
        file_path = os.path.join(self.extraction_dir, file)
        return os.path.exists(file_path)

    def _filter_missing_files(self, unfiltered):
        filtered = {}
        for key, item in unfiltered.items():
            if self._file_exists(item['ori']):
                filtered[key] = item

        return filtered

    def _filter_missing_images(self, unfiltered):
        filtered = {}
        for key, item in unfiltered.items():
            logos = []
            for logo in item:
                if not logo.get('ori', None):
                    continue
                if self._file_exists(logo['ori']):
                   logos.append(logo)
            if len(logos):
                filtered[key] = logos

        return filtered


