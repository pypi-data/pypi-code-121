from pypers.steps.base.step_generic import EmptyStep
import re
import os


class Join(EmptyStep):
    """
    Joins 2 inputs into one output
    """
    spec = {
        "version": "0.1",
        "descr": [
            "Returns the grouped output"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "archives",
                    "type": "list",
                    "descr": "the archives to extract grouped by extraction date",
                }
            ],
            "outputs": [
                {
                    "name": "archives",
                    "type": "list",
                    "descr": "the archives to extract grouped by extraction date",
                }
            ],
            "params": [
                {
                    "name": "mask_input",
                    "type": "str",
                    "value": ".*"
                },
                {
                    "name": "mask_output",
                    "type": "str",
                    "value": ".*"
                }
            ]
        }
    }

    def process(self):
        archives_per_date = {}
        r = re.compile(self.mask_input)
        for archive in self.archives:
            filename = os.path.basename(archive[1])
            archive_name = r.sub(self.mask_output, filename)

            if archive[0] not in archives_per_date.keys():
                archives_per_date[archive[0]] = {
                    'name': archive_name,
                    'archives': []
                }
            archives_per_date[archive[0]]['archives'].append(archive[1])

        self.archives = []
        for date in sorted(archives_per_date.keys()):
            self.archives.append((date, archives_per_date[date]))
