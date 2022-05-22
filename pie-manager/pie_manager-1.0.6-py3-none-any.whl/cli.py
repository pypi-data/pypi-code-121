from colorama import Fore, init
import os, shutil, sys
import requests

init(convert=True)

def parent_dir(path: str):
    return os.path.abspath(os.path.join(path, os.pardir))

def main():
    pie = shutil.which("pie")
    if pie is not None:
        os.remove(pie)

    pie_manager_path = shutil.which("pie-manager")
    if pie_manager_path is not None:
        print(Fore.RED + "Please reinstall Pie Manager." + Fore.RESET)
        exit()

    new_pie = parent_dir(pie)

    # if os is windows
    if os.name == "nt":
        install_link = "https://github.com/skandabhairava/pie-rust/releases/download/main/windows-pie.exe"
        extension = ".exe"
    # if os is linux
    elif os.name == "posix":
        install_link = "https://github.com/skandabhairava/pie-rust/releases/download/main/linux-pie"
        extension = ""
    # if os is mac
    elif os.name == "mac":
        install_link = "https://github.com/skandabhairava/pie-rust/releases/download/main/macos-pie"
        extension = ""

    #install pie from link into pie-manager directory
    print(Fore.GREEN + "Installing Pie..." + Fore.RESET)
    r = requests.get(install_link, stream=True)
    with open(new_pie+extension, "wb") as f:
        f.write(r.content)
    os.chmod(new_pie, 0o755)
        
def many_in_check(*list, iterable=None):
    if iterable is None:
        return False

    for item in iterable:
        if item in list:
            return True

    return False

if __name__ == "__main__":
    if many_in_check("-U", "--upgrade", "--install", "-I", iterable=(i.lower() for i in sys.argv)):
        main()
        exit()

    print(Fore.RED + "Please use '--upgrade' '-U', '--install', '-I' to install/upgrade pie." + Fore.RESET)