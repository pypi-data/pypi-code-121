import os, platform, ctypes

def clear():
    system = platform.system()
    if system == 'Windows':
        os.system('cls')
    elif system == 'Linux':
        os.system('clear')
    else:
        print('\n')*120
    return

def setTitle(str):
    system = platform.system()
    if system == 'Windows':
        ctypes.windll.kernel32.SetConsoleTitleW(f"{str} | CookiesKush420#5391")
    else:
        os.system(f"\033]0;{str} | CookiesKush420#5391\a")

