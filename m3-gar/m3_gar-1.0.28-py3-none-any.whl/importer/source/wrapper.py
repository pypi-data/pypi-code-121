import datetime
import os
import shutil
from pathlib import (
    Path,
)


class SourceWrapper:
    source = None

    def __init__(self, source, **kwargs):
        pass

    def get_date_info(self, filename):
        date_str = filename.split('_')[-2]
        return datetime.datetime.strptime(date_str, '%Y%m%d').date()

    def get_file_list(self):
        raise NotImplementedError()

    def open(self, filename):
        raise NotImplementedError()

    def __getstate__(self):
        state = self.__dict__.copy()

        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


class DirectoryWrapper(SourceWrapper):
    is_temporary = False

    def __init__(self, source, is_temporary=False, **kwargs):
        super().__init__(source=source, **kwargs)
        self.is_temporary = is_temporary
        self.source = os.path.abspath(source)

    def get_file_list(self):
        source = Path(self.source)

        return [
            str(filepath.relative_to(source))
            for filepath
            in source.glob('**/*')
            if filepath.is_file()
        ]

    def get_full_path(self, filename):
        return os.path.join(self.source, filename)

    def open(self, filename):
        return open(self.get_full_path(filename), 'rb')

    def __del__(self):
        if self.is_temporary:
            shutil.rmtree(self.source, ignore_errors=True)


class LocalArchiveWrapper(SourceWrapper):

    def __init__(self, source, **kwargs):
        super().__init__(source=source, **kwargs)
        self.source = source

    def get_file_list(self):
        return self.source.namelist()

    def open(self, filename):
        return self.source.open(filename)

    def __getstate__(self):
        state = super().__getstate__()

        state['source'] = (self.source.__class__, self.source.filename)

        return state

    def __setstate__(self, state):
        source_class, source_filename = state['source']
        state['source'] = source_class.open_file(source_filename)

        super().__setstate__(state)
