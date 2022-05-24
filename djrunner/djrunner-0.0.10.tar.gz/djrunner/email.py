
import os

from datetime import datetime

from django.core.mail.backends.filebased import EmailBackend


class FileBasedEmailBackend(EmailBackend):

    def _get_filename(self):
        if self._fname is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            name = "%s-%s.eml" % (timestamp, abs(id(self)))
            self._fname = os.path.join(self.file_path, name)
        return self._fname
