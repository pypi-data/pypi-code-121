import subprocess, requests
from time import sleep
from colorama import Fore
import os, platform, ctypes, requests

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
        ctypes.windll.kernel32.SetConsoleTitleW(f"{str} | CookiesKush420#4251")
    else:
        os.system(f"\033]0;{str} | Made By Cookies_Kush420#6969\a")

def auth(str):
    site = requests.get(str)
    hardwareid = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
    try:
        if hardwareid in site.text:
            pass
        else:
            setTitle(f'Error Authentication Failed!')
            print(f'{Fore.RESET}[{Fore.LIGHTRED_EX}ERROR{Fore.RESET}] {Fore.LIGHTRED_EX}HWID NOT in database')
            print(f'{Fore.RESET}[{Fore.GREEN}HWID{Fore.RESET}:' + hardwareid + ']')
            sleep(5)
            exit()
    except:
        print(f'{Fore.RESET}[{Fore.LIGHTRED_EX}ERROR{Fore.RESET}] {Fore.LIGHTRED_EX}FAILED to connect to database, Please contact the owner to give you AUTH to access this product')
        sleep(5) 
        exit() 
    
    setTitle('Authentication Success')
    print(f'{Fore.GREEN}Authentication Success loading launcher{Fore.RESET}. . .')
    sleep(2)
    clear()


