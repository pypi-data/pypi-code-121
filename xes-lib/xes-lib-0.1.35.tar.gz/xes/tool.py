import subprocess
import os
import platform

def desk():
    if platform.system() == "Darwin":
        return os.path.expanduser("~/Desktop/")
    elif platform.system() == "Windows":
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        return winreg.QueryValueEx(key, "Desktop")[0] + "/"
    else:
        return os.path.expanduser("~/Desktop/")

def xopen(file_name=None):
    if file_name:
        new_path = desk() + file_name
        if not os.path.exists(new_path):
            os.mkdir(new_path)
    else:
        new_path = os.getcwd()

    if platform.system() == "Windows":
        os.startfile(new_path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", new_path])
    else:
        subprocess.Popen(["xdg-open", new_path])

    return new_path + "/"