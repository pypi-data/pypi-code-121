from random import randint
from time import sleep


def generate_random_time(start=10, end=30, display=False):
    time = randint(start, end)
    if display:
        print(f'> Esperando {time} segundos')
    sleep(time)