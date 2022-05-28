from logging import exception, info
from pathlib import Path
from threading import Thread, Semaphore

import win32con
import win32event
import win32file


class DirectoryObservable(Thread):
    """
    Notifies observers on directory change
    """
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __init__(self,
                 path: str,
                 observers: list = (),
                 timeout: int = win32event.INFINITE,
                 watch_sub_directories: bool = False,
                 change_flag=win32con.FILE_NOTIFY_CHANGE_LAST_WRITE):
        """
        :param path: File or directory to observe
        :param observers: List of observer functions
        :param timeout: Timeout for event; Infinite by default
        :param watch_sub_directories: True if changes in sub-directories should be observed
        :param change_flag: Flag specifying what changes to watch
        """
        Thread.__init__(self, daemon=True)
        self._list_semaphore = Semaphore(value=1)
        self._observers = list(observers)
        self._path = Path(path).absolute()
        if not self._path.exists():
            raise FileNotFoundError
        self._path = str(self._path)
        self._timeout = timeout  # Only get notify on detected change
        # """https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-findfirstchangenotificationa"""
        self._change_handle = win32file.FindFirstChangeNotification(self._path, watch_sub_directories, change_flag)
        self._active = True
        info(f'Change handle {self._change_handle}')

    def add_observer(self, update_function: callable) -> None:
        """
        Add observer function. The function is called on detected directory change with path as argument
        :param update_function: Callback function
        """
        with self._list_semaphore:
            self._observers.append(update_function)

    def remove_observer(self, update_function: callable) -> bool:
        """
        Observe path, and call function on change
        :param update_function: Callback function
        :return: True, if update_function was removed, False otherwise
        """
        with self._list_semaphore:
            if update_function in self._observers:
                self._observers.remove(update_function)
                return True
        return False

    def _notify_observers(self) -> None:
        """
        Notify all observers about directory change
        """
        with self._list_semaphore:
            for update_function in self._observers:
                update_function(self._path)

    def stop(self, timeout: float = None) -> None:
        """
        Stop the active thread
        :param timeout: Timeout for joining the thread in seconds
        """
        if self.is_alive():
            self._active = False
            info('CLOSE OBSERVABLE')
            win32file.FindCloseChangeNotification(self._change_handle)
            super().join(timeout)

    def run(self) -> None:
        """
        run() function is started on Thread.start().
        """
        while self._active:
            try:
                # """https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject"""
                result = win32event.WaitForSingleObject(self._change_handle, self._timeout)
                info(f'Event: {result}')
                if not self._active:
                    return
                if result == win32con.WAIT_OBJECT_0:
                    self._notify_observers()
                    win32file.FindNextChangeNotification(self._change_handle)
            except Exception as e:
                exception(e)
