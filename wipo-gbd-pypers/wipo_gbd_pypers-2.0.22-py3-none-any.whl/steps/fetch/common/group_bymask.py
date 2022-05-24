import os
import re
from pypers.utils.archive_dates import ArchiveDateManagement

from pypers.steps.base.step_generic import EmptyStep


class GroupByMask(EmptyStep):
    """
    Grouping and sorting a list of archives by applying a mask to their name
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns a list of sorted dictionary with key=masked "
            "and value=/path/to/archive"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "input_files",
                    "type": "file",
                    "descr": "the files to apply renaming mask on"
                }
            ],
            "params": [
                {
                    "name": "mask_input",
                    "type": "str",
                    "descr": "the mask to match the parts of the input filename"
                },
                {
                    "name": "mask_output",
                    "type": "str",
                    "descr": "how to rearrange the name based on mask"
                }

            ],
            "outputs": [
                {
                    "name": "output_files",
                    "descr": "the dictionary with renamed keys"
                }
            ]
        }
    }

    def process(self):
        self.output_files = []
        r = re.compile(self.mask_input)

        grouped_files = {}
        for input_file in self.input_files:
            input_filename = os.path.splitext(os.path.basename(input_file))[0]

            matches = r.search(input_filename)

            if not matches:
                raise Exception('could not apply renaming mask %s on %s. '
                                'order is not guaranteed. '
                                'aborting!' % (self.mask_input,
                                               input_filename))

            masked_filename = r.sub(self.mask_output, input_filename)

            # if masked_filename.isdigit():
            #     masked_filename = int(masked_filename)

            # for special cases like frtm, we have an archive year and weeknb
            # use this method to tranlate to a date
            office_extraction_date = ArchiveDateManagement(
                self.collection, masked_filename).archive_date


            grouped_files.setdefault(office_extraction_date, [])
            grouped_files[office_extraction_date].append(input_file)

        # grouped_files = { 'yyyy-mm-dd': ['archA', 'archB'], 'yyyy-mm-dd': ['archC', 'archD'] }

        grouped_files_list = []
        for key, files in grouped_files.items():
            group = {}
            group[key] = files
            grouped_files_list.append(group)

        # sort list by date (masked file name)
        grouped_files_list = sorted(grouped_files_list,
                                    key=lambda k: next(iter(k)))

        # grouped_files_list = [ { 'yyyy-mm-dd': ['archA', 'archB'] } , { 'yyyy-mm-dd': ['archC', 'archD'] } ]

        # transform to list of tuples
        # [('yyyy-mm-dd', 'archA'), ('yyyy-mm-dd', 'archB'), ('yyyy-mm-dd', 'archC')]
        for key_files in grouped_files_list:
            for key in key_files.keys():
                for file in sorted(key_files[key]):
                    self.output_files.append((key, file))

