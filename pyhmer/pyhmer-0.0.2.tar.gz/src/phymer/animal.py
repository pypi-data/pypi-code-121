from pathlib import Path
import csv
import random


def generate_rhyme_list(path):
    rhymes = []
    with open(path) as file:
        csv_file = csv.reader(file)
        for row in csv_file:
            rhymes.append(row)
    return rhymes
animal_rhymes_path = Path('animal_rhymes.csv')
animal_rhymes_list = generate_rhyme_list(animal_rhymes_path)

def get_animal_rhyme(animal_rhymes_list):
    rhyme = random.choice(animal_rhymes_list)
    return rhyme