import subprocess, requests
from time import sleep
from colorama import Fore
from .common import *




def auth(str):
    setTitle("Authentication In Progress")
    print(f"{Fore.LIGHTYELLOW_EX}Authenticating, {Fore.RESET}please wait. . .")
    site = requests.get(str)
    hardwareid = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
    try:
        if hardwareid in site.text:
            pass
        else:
            setTitle(f'Error Authentication Failed!')
            print(f'{Fore.RESET}[{Fore.LIGHTRED_EX}ERROR{Fore.RESET}] {Fore.LIGHTRED_EX}HWID NOT in database{Fore.RESET}')
            print(f'{Fore.RESET}[{Fore.GREEN}HWID{Fore.RESET}:' + f'{Fore.LIGHTRED_EX}{hardwareid}{Fore.RESET}' + f']{Fore.RESET}')
            sleep(5)
            exit()
    except:
        print(f'{Fore.RESET}[{Fore.LIGHTRED_EX}ERROR{Fore.RESET}] {Fore.LIGHTRED_EX}FAILED to connect to database, Please contact the owner to give you AUTH to access this product{Fore.RESET}')
        sleep(5) 
        exit() 
    
    setTitle('Authentication Success')
    print(f'{Fore.GREEN}Authentication Success loading launcher{Fore.RESET}. . .')
    sleep(2)
    clear()