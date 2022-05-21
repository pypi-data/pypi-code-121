import subprocess
import sys
from pathlib import Path
from time import time

from .config import ENVIRONMENT, REPO_BRANCH, REPO_URL
from .yolov5_utils.general import emojis


def install_dependencies():
    t = time()
    print(emojis('Installing YOLOv5 🚀 requirements...'), end=" ")
    s = ['pip', 'install', '-r', 'yolov5/requirements.txt']
    if ENVIRONMENT == 'development':
        subprocess.call(s)
    else:
        subprocess.call(s, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f'Done ({time() - t:.1f}s)')


def clone_yolo():
    """
    Check that YOLOv5 is on the system and clone if not found
    """
    CWD = str(Path('.').resolve())  # current working directory
    if CWD not in sys.path:
        sys.path.append(CWD)  # add CWD to PATH

    if not Path("./yolov5").is_dir():
        from git import Repo
        try:
            t = time()
            print(emojis(f"Cloning YOLOv5 🚀 from {REPO_URL}..."), end=" ")
            Repo.clone_from(REPO_URL, "yolov5", branch=REPO_BRANCH)  # Temp solution while waiting on pull request
            print(f'Done ({time() - t:.1f}s)')
            install_dependencies()

        except Exception as e:
            print(f"ERROR: Failed to clone YOLOv5: {e}")


class YOLOv5Wrapper:

    @staticmethod
    def export(**kwargs):
        """Calls the YOLOv5 export module"""
        import yolov5.export as _export
        _export.run(**kwargs)

    @staticmethod
    def detect(**kwargs):
        """Calls the YOLOv5 detect module"""
        import yolov5.detect as _detect
        _detect.run(**kwargs)

    @staticmethod
    def train(callback_handler, **kwargs):
        """Calls the YOLOv5 train module"""
        import yolov5.train as _train
        opt = _train.parse_opt(True)
        for k, v in kwargs.items():
            setattr(opt, k, v)

        # _train.run(**kwargs)
        # text_trap = io.StringIO()
        # sys.stdout = text_trap # Trap output
        _train.main(opt, callback_handler)
        # sys.stdout = sys.__stdout__ # Restore output

    @staticmethod
    def new_callback_handler():
        """Returns a YOLOv5 callback handler"""
        from yolov5.utils.callbacks import Callbacks  # assume yolov5/ in cwd
        return Callbacks()
