import os
import glob
from pypers.steps.base.step_generic import EmptyStep


class Manifests(EmptyStep):
    """
    Orders manifets base on office_extraction_date
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
                    "name": "manifest_list",
                    "descr": "the manifest list",
                }
            ]
        }
    }

    # manifest_file: ORIFILES_DIR/run_id/type/collection/office_extraction_date/archive_name/manifest.json
    def _sort_by_extraction_date_and_archive_name(self, manifest_file):
        manifest_path = os.path.dirname(manifest_file)

        office_extraction_date, archive_name = manifest_path.split(os.sep)[-2:]
        return '%s.%s' % (office_extraction_date, archive_name)

    def process(self):

        # look for manifest.json files under this path
        # ORIFILES_DIR/run_id/type/collection/office_extraction_date/archive_name

        ori_path = os.path.join(os.environ.get('ORIFILES_DIR'), # mandatory ENV VARIABLE - we do not want to make defaults
                                self.run_id,
                                self.pipeline_type,
                                self.collection.replace('harmonize_', ''))

        manifests_path = os.path.join(ori_path, '*', '*', 'manifest.json')
        manifests_files = list(glob.glob(manifests_path))

        manifests_files.sort(key=self._sort_by_extraction_date_and_archive_name)

        self.manifest_list = manifests_files
