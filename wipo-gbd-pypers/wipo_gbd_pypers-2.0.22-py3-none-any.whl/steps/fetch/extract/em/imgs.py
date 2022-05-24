import os
import re
from pypers.steps.base.step_generic import EmptyStep
from pypers.utils import utils


class Images(EmptyStep):
    """
    Extract EMID IMGS archives
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
                    "name": "input_archive",
                    "type": "file",
                    "descr": "the archives to extract"
                }
            ],
            "outputs": [
                {
                    "name": "dest_dir",
                    "descr": "the directory containing img extractions"
                }
            ],
        }
    }

    def process(self):

        self.archive_name = []

        for archive in self.input_archive:
            archive_name, archive_ext = os.path.splitext(
                os.path.basename(archive))

            self.logger.info('%s\n%s\n' % (archive, re.sub(r'.', '-', archive)))
            self.logger.info('extracting into %s\n' % (self.output_dir))
            if archive_ext.lower() == '.zip':
                utils.zipextract(archive, self.output_dir)
            elif archive_ext.lower() == '.tar':
                utils.tarextract(archive, self.output_dir)
            else:
                raise Exception('Unsupported archive type [%s]' % archive_ext)
            self.archive_name.append(archive_name)
        self.dest_dir = [self.output_dir]
