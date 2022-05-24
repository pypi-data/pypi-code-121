from pypers.core.step import FunctionStep


class FTP(FunctionStep):
    spec = {
        "version": "0.1",
        "descr": [
            "Fetch archives from either a local dir or FTP server"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "keyboard",
                    "type": "int"
                }
            ],
            "params": [
                {
                    "name": "limit",
                    "type": "int",
                },

            ],
            "outputs": [
                {
                    "name": "output_files",
                    "type": "file",
                    "descr": "output file names"
                }
            ]
        }
    }

    def process(self):
        return
