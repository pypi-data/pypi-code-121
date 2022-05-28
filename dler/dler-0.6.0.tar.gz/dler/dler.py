
from .tasker import BaseTasker, conver_tasker
from .tasker.exceptions import FileExistsException

class Dler:
    tasker: BaseTasker
    def __init__(self, url: str, **kwargs):
        self.tasker = conver_tasker(url, **kwargs)

    def run(self):
        try:
            self._run()
        except FileExistsException:
            filename = self.tasker.filepath
            print(f"{filename} 已经下载")
        except:
            import traceback
            traceback.print_exc()
            traceback.print_stack()

    def _run(self):
        """运行

        """
        self.tasker.check_file_exists()
        self.tasker.before_build()
        self.tasker.build()
        self.tasker.before_run()
        self.tasker.run()
        self.tasker.after_run()
        self.tasker.clear()
