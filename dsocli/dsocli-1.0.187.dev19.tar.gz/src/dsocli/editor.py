from subprocess import Popen, PIPE
from .logger import Logger
from .settings import *
from .file_utils import *
from .settings import *


def get_editor():
    if WIN_PLATFORM:
        return WindowsEditor()
    else:
        return PosixEditor()

class EditorBase(object):

    @property
    def EDITOR(self):
        return None

    def _get_editor_cmdline(self):
        editor = EDITOR or self.EDITOR
        return editor.split(' ')  ### IMPROVEME using shellex


    def _check_editor_cmdline(self, filename):
        pass



    def edit(self, filename):
        self._check_editor_cmdline(filename)

        with open(self.filename, 'r+b') as f:
            oldContent = f.read()
        returnCode = self._popen(self.cmdline)
        if not returnCode == 0:
            raise DSOException(f"Edit failed with exit code '{returnCode}'.")
        with open(self.filename, 'r+b') as f:
            newContent = f.read()
        changed = not newContent == oldContent
        newContent = newContent.decode('utf-8')
        ### get rid of extra '\n' appended by editors on MacOS, not tested on Linux and Win
        if newContent and newContent[-1] == '\n':
            newContent = newContent[0:len(newContent)-1]
        return newContent, changed


    def _popen(self, *args, **kwargs):
        return Popen(*args, **kwargs).wait()


class PosixEditor(EditorBase):

    @property
    def EDITOR(self):
        return 'nano'

    def _check_editor_cmdline(self, filename):
        self.cmdline = self._get_editor_cmdline()
        if not exists_on_path(self.cmdline[0]):
            raise DSOException(f"Editor '{self.cmdline[0]}' not found in PATH.")
        self.cmdline.append(filename)
        self.filename = filename

class WindowsEditor(EditorBase):

    @property
    def EDITOR(self):
        return 'nano'

    def _popen(self, *args, **kwargs):
        kwargs['shell'] = True
        return Popen(*args, **kwargs).wait()

    def _check_editor_cmdline(self, filename):
        self.cmdline = self._get_editor_cmdline()
        if not (exists_on_path(f"{self.cmdline[0]}.exe") or exists_on_path(f"{self.cmdline[0]}.com")):
            raise DSOException(f"Editor '{self.cmdline[0]}' not found in PATH.")
        self.cmdline.append(filename)
        self.filename = filename


Editor = get_editor()
