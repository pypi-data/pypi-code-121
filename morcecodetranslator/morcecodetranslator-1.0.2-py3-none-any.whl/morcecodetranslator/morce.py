import re

__all__ = ['encript', 'decript']

class MorceCodeTranslator:
    '''
    Morce code translator convert text to morce code and vice versa.
    Its follow below algorithm for the convertion as per the morce-code,
        1. Single space for same char follows
        2. Three spaces for different char
        3. Seven spaces to differentiate the word
    '''
    def __init__(self):
        self.__MORCE_CODE = {
            'A': '.-',
            'B': '-...',
            'C': '-.-.',
            'D': '-..',
            'E': '.',
            'F': '..-.',
            'G': '--.',
            'H': '....',
            'I': '..',
            'J': '.---',
            'K': '-.-',
            'L': '.-..',
            'M': '--',
            'N': '-.',
            'O': '---',
            'P': '.--.',
            'Q': '--.-',
            'R': '.-.',
            'S': '...',
            'T': '-',
            'U': '..-',
            'V': '...-',
            'W': '.--',
            'X': '-..-',
            'Y': '-.--',
            'Z': '--..',
            '1': '.----',
            '2': '..---',
            '3': '...--',
            '4': '....-',
            '5': '.....',
            '6': '-....',
            '7': '--...',
            '8': '---..',
            '9': '----.',
            '0': '-----'
        }

    def encript(self, message) -> str:
        '''
        Encript text to morce code

        :param message: message for convert to morce code
        :return: morce code
        '''

        morce_code = ''
        _pre_char = None

        for char in str(message).upper():
            # Evaluating space to seperate the word
            if char == ' ':
                morce_code += '       '
                # reset the previous char to None
                # To avoid append space to the morce code 
                # on the next word cycle
                _pre_char = None
                continue
            # Checking previous char is current char
            # To add spaces based on the morce algorithm
            if _pre_char:
                if str(_pre_char).__eq__(char):
                    morce_code += ' '
                else:
                    morce_code += '   '
            morce_code += self.__MORCE_CODE.get(char)
            _pre_char = char
        return morce_code

    def decript(self, morce_code) -> str:
        '''
        Decripting the morce code to text

        :param morce_code: morce code for convert to text
        :return: Plain text of equalant morce code
        '''
        message = ''

        # Spliting the morce based more than 4 spaces
        # So its exactly split the words
        mc_li = re.split(r'\s\s\s\s+', morce_code)
        for mc in mc_li:
            if mc == '':
                continue
            codes = re.split(r'\s+', mc)
            for code in codes:
                idx = list(self.__MORCE_CODE.values()).index(code)
                message += list(self.__MORCE_CODE.keys())[idx]
            message += ' '
        return message.removesuffix(' ')


# if __name__ == '__main__':
#     mct = MorceCodeTranslator()
#     print(mct.encript('MORCE CODE'))
#     print(mct.decript('--   ---   .-.   -.-.   .       -.-.   ---   -..   .'))
