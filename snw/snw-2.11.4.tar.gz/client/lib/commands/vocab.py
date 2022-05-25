import os
import sys

import requests

from lib import utils


class Vocab:
    def __init__(self, options, auth):
        self.options = options
        self.auth = auth
        self.is_json = self.options.display == "JSON"

    def detail(self):
        res = utils.show_model_files_list(url=self.options.url, auth=self.auth,
                                          model_name=self.options.model,
                                          directory=self.options.directory)
        return res

    def get(self):
        with open(os.path.expanduser(self.options.output), 'w+') \
                if self.options.output else sys.stdout as output:
            r = requests.get(os.path.join(self.options.url, "model/getfile/",
                                          self.options.vocab, self.options.file),
                             auth=self.auth)
            if r.status_code != 200:
                raise RuntimeError('incorrect result from \'model/getfile\' service: %s' % r.text)

            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:
                    if self.options.output:
                        output.write(chunk)
                    else:
                        utils.write_to_stdout(chunk)
            sys.exit(0)

    def execute_command(self):
        result = None
        if self.options.subcmd == "detail":
            result = self.detail()
        if self.options.subcmd == "get":
            result = self.get()
        return result
