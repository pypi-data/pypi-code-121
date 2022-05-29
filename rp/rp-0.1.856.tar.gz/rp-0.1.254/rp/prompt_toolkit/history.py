from __future__ import unicode_literals
from abc import ABCMeta, abstractmethod
from six import with_metaclass

import datetime
import os

__all__ = (
    'FileHistory',
    'History',
    'InMemoryHistory',
)


class History(with_metaclass(ABCMeta, object)):
    """
    Base ``History`` interface.
    """
    @abstractmethod
    def append(self, string):
        " Append string to history. "

    @abstractmethod
    def __getitem__(self, key):
        " Return one item of the history. It should be accessible like a `list`. "

    @abstractmethod
    def __iter__(self):
        " Iterate through all the items of the history. Cronologically. "

    @abstractmethod
    def __len__(self):
        " Return the length of the history.  "

    def __bool__(self):
        """
        Never evaluate to False, even when the history is empty.
        (Python calls __len__ if __bool__ is not implemented.)
        This is mainly to allow lazy evaluation::

            x = history or InMemoryHistory()
        """
        return True

    __nonzero__ = __bool__  # For Python 2.


class InMemoryHistory(History):
    """
    :class:`.History` class that keeps a list of all strings in memory.
    """
    def __init__(self):
        self.strings = []

    def append(self, string):
        self.strings.append(string)

    def __getitem__(self, key):
        return self.strings[key]

    def __iter__(self):
        return iter(self.strings)

    def __len__(self):
        return len(self.strings)


class FileHistory(History):
    """
    :class:`.History` class that stores all strings in a file.
    """
    def __init__(self, filename):
        self.strings = []
        self.filename = filename

        self._load()

    def _load(self):
        #took .2 seconds with 18000 items in history; 
        # from rp import sleep,tic,toc,ptoc,ptoctic,ring_terminal_bell,run_as_new_thread,text_to_speech
        from rp import run_as_new_thread
        # ring_terminal_bell()
        # tic()

        lines = []

        def add():
            if lines:
                # Join and drop trailing newline.
                string = ''.join(lines)[:-1]

                self.strings.append(string)

        def add_all_lines():
            nonlocal lines
            if os.path.exists(self.filename):
                with open(self.filename, 'rb') as f:
                    for line in f:
                        # print(line)
                        line = line.decode('utf-8')

                        if line.startswith('+'):
                            lines.append(line[1:])
                        else:
                            add()
                            lines = []
                    add()
            # text_to_speech("a")
        # if os.path.exists(self.filename):
        #     with open(self.filename, 'rb') as f:
        #         for line in f:
        #             line = line.decode('utf-8')

        #             if line.startswith('+'):
        #                 lines.append(line[1:])
        #             else:
        #                 add()
        #                 lines = []
        #         add()
        run_as_new_thread(add_all_lines)#Running this as a new thread will save .2 seconds with my 18000 items in history
        # ptoctic()
        # sleep(3)
        # ring_terminal_bell()

    def append(self, string):
        self.strings.append(string)

        # Save to file.
        with open(self.filename, 'ab') as f:
            def write(t):
                f.write(t.encode('utf-8'))
            
            write('\n# %s\n' % datetime.datetime.now())
            for line in string.split('\n'):
                write('+%s\n' % line)

    def __getitem__(self, key):
        return self.strings[key]

    def __iter__(self):
        return iter(self.strings)

    def __len__(self):
        return len(self.strings)
