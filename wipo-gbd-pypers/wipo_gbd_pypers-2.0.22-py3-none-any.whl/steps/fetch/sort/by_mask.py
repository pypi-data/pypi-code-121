import os
import re
from pypers.steps.base.step_generic import EmptyStep


class SortByMask(EmptyStep):
    """
    Sorting a list of archives by applying a mask to their name
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

        for input_file in self.input_files:
            input_filename = os.path.splitext(os.path.basename(input_file))[0]

            matches = r.search(input_filename)

            if not matches:
                raise Exception('could not apply renaming mask %s on %s. '
                                'order is not guaranteed. '
                                'aborting!' % (self.mask_input,
                                               input_filename))
            masked_filename = r.sub(self.mask_output, input_filename)

            if masked_filename.isdigit():
                masked_filename = int(masked_filename)

            mask = {}
            mask[masked_filename] = input_file
            self.output_files.append(mask)

        # sort by masked file name
        self.output_files = sorted(self.output_files,
                                   key=lambda k: next(iter(k)))

