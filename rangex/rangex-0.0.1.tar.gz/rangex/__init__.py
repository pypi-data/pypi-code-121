import random


letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G',
           'H', 'I', 'J', 'K', 'L', 'M', 'N',
           'O', 'P', 'Q', 'R', 'S', 'T', 'U',
           'V', 'W', 'X', 'Y', 'Z', '0', '1',
           '2', '3', '4', '5', '6', '7', '8',
           '9']

asciis = ['a', 'b', 'c', 'd', 'e', 'f', 'g',
          'h', 'i', 'j', 'k', 'l', 'm', 'n',
          'o', 'p', 'q', 'r', 's', 't', 'u',
                    'v', 'w', 'x', 'y', 'z']

key = '\\'

class randomizer():
    @classmethod
    def single(self, string: str):
        for i in asciis: string = string.replace(f'{key}{i}', str(random.choice(letters)))
        return string

    @classmethod
    def multi(self, string: str, repeat: int):
        return [self.single(string) for i in range(repeat)]
