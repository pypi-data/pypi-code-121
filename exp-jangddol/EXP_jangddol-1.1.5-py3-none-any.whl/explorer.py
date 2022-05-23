import os
import subprocess
import platform


def Shvar_open():
    if platform.system() == 'Windows':
        FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
        Directory = __file__.replace("\\explorer.py", "")
        path = os.path.normpath(Directory)
        if os.path.isdir(path):
            subprocess.run([FILEBROWSER_PATH, path])
        elif os.path.isfile(path):
            subprocess.run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)])
    else:
        Directory = __file__.replace('/explorer.py', '')
        print("If OS is not Window, this function is not available")
        print("PATH : " + Directory)
