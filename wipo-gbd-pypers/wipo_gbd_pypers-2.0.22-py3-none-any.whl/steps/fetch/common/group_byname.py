from itertools import chain
from pypers.steps.base.step_generic import EmptyStep


class GroupByName(EmptyStep):
    """
    Group update archives by name
    """
    spec = {
        "version": "0.1",
        "descr": [
            "Returns the archives grouped by name"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "input_files",
                    "type": "file",
                    "descr": "the archives fetched by the fetch step"
                }
            ],
            "outputs": [
                {
                    "name": "output_files",
                    "descr": "the sorted list"
                }
            ],
        }
    }

    def process(self):
        self.output_files = []

        udates = [file.keys() for file in self.input_files]
        udates = list(chain.from_iterable(udates))
        udates = sorted(list(set(udates)))

        def _concat(item, lst=[]):
            if isinstance(item, list):
                lst += item
            else:
                lst.append(item)
            return lst

        for udate in udates:
            indate = {}
            indate[udate] = []
            for infile in self.input_files:
                inkey = next(iter(infile))
                if inkey == udate:
                    indate[udate] = _concat(infile[inkey], lst=indate[udate])
                    self.logger.info('  > %s' % infile[inkey])

            self.output_files.append(indate)
