import os
from pypers.steps.base.step_generic import EmptyStep


class SortByName(EmptyStep):
    """
    Sorting a list of archives by their name
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns a list of sorted dictionary with key=name and value=/path/to/archive"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "input_files",
                    "type": "file",
                    "descr": "the files to sort"
                }
            ],
            "outputs": [
                {
                    "name": "output_files",
                    "descr": "the sorted list"
                }
            ]
        }
    }

    def process(self):
        self.output_files = []
        for input_file in self.input_files:
            input_filename = os.path.splitext(os.path.basename(input_file))[0]
            dict = {}
            dict[input_filename] = input_file
            self.output_files.append(dict)

        # sort by file name
        self.output_files = sorted(self.output_files,
                                   key=lambda k: next(iter(k)))

