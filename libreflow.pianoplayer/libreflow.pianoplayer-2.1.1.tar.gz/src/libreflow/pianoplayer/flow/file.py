import pathlib

from libreflow.baseflow.file import (
    CreateFileAction       as BaseCreateFileAction,
    CreateFolderAction     as BaseCreateFolderAction,
    FileSystemMap          as BaseFileSystemMap
)
from libreflow.utils.flow import get_contextual_dict


class CreateFileAction(BaseCreateFileAction):

    def run(self, button):
        if button == 'Cancel':
            return

        name, extension = self.file_name.get(), self.file_format.get()

        if self._files.has_file(name, extension):
            self._warn((
                f'File {name}.{extension} already exists. '
                'Please choose another name.'
            ))
            return self.get_result(close=False)
        
        # Create a file with the default path format this
        # project is supposed to provide
        self._files.add_file(
            name,
            extension=extension,
            base_name=name,
            display_name=f'{name}.{extension}',
            tracked=self.tracked.get(),
        )
        self._files.touch()


class CreateFolderAction(BaseCreateFolderAction):

    def run(self, button):
        if button == 'Cancel':
            return
        
        name = self.folder_name.get()

        if self._files.has_folder(name):
            self._warn((
                f'Folder {name} already exists. '
                'Please choose another name.'
            ))
            return self.get_result(close=False)
        
        # Create a folder with the default path format this
        # project is supposed to provide
        self._files.add_folder(
            name,
            base_name=name,
            display_name=name,
            tracked=self.tracked.get(),
        )
        self._files.touch()


class FileSystemMap(BaseFileSystemMap):
    
    def add_file(self, name, extension, display_name=None, base_name=None, tracked=False, default_path_format=None):
        if default_path_format is None:
            default_path_format = get_contextual_dict(self, 'settings').get(
                'path_format', None
            )
        return super(FileSystemMap, self).add_file(name, extension, display_name, base_name, tracked, default_path_format)

    def add_folder(self, name, display_name=None, base_name=None, tracked=False, default_path_format=None):
        if default_path_format is None:
            default_path_format = get_contextual_dict(self, 'settings').get(
                'path_format', None
            )
        return super(FileSystemMap, self).add_folder(name, display_name, base_name, tracked, default_path_format)
