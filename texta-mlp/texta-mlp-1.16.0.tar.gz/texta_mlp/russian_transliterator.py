import regex as re


class Transliterate():
    """
    Transliterate class to transliterate text from Cyrillic to Latin

    Ruleset: http://www.eki.ee/books/ekk09/index.php?id=37&p=2&p1=6
    'Vene keele tähestikust eesti tähestikku' 2005.

    Usage:
        Initialize the class:
            foo = Transliterate()
        Call with a list of sentences you'd like to transliterate:
            foo(['Дженни играет с мяц.', 'Яне говорит на телефоне.', 'Рассекречены планы выпуска дешевого iPhone Читать далее'])
            # This Returns -- ['Дженни играет с мяц.', 'Яне говорит на телефоне.', 'Рассекречены планы выпуска дешевого iPhone Читать далее']
    """

    def __call__(self, sentences):
        return self._transliterate(sentences)

    def _transliterate(self, sentences):
        """The main transliteration processor

        Arguments:
            sentences {list of strings} -- A list of string sentences to tranliterate

        Returns:
            [list of strings] -- A transliterated version of the output sentences
        """
        new_sentences = []
        for sentence in sentences:
            converted_sentence = []
            sentence = sentence.split(' ')
            for word in sentence:
                word = self._check_doublechar_rules(word)
                converted_word = ''
                for char_index, char in enumerate(word):
                    transchar = ''
                    if char in self._translit_table:
                        transchar = self._translit_table[char]
                    elif char in self._chars_with_rules:
                        transchar = self._check_char_rules(
                            word, char, char_index)
                    else:
                        transchar = char

                    converted_word += transchar
                converted_sentence.append(converted_word)
            new_sentences.append(' '.join(converted_sentence))

        return new_sentences

    def _check_doublechar_rules(self, word):
        """Checks for doublechar rules, currently only for the cyr characters ij

        Arguments:
            word {string} -- The word in which to check the rule in

        Returns:
            [string] -- The modified version of the input word relative to the rules, if no rules were found, returns the unchanged input word.
        """
        word_to_return = word
        if len(word) > 3:
            for match in re.finditer("ий", word.lower()):
                if match.span()[1] - 1 == len(word) - 1:
                    new_char = self._check_if_upper_and_return(
                        word[match.span()[0]], 'I')
                    word_to_return = list(word_to_return[:match.span()[0] + 1])
                    word_to_return[-1] = new_char
                    word_to_return = ''.join(word_to_return)

        return word_to_return

    def _check_char_rules(self, word, char, char_index):
        """Checks for specific rules for the given transliteration

        Arguments:
            word {string} -- The word in which the character originated from.
            char {string} -- The character about to be transliterated.
            char_index {int} -- The index of the character in the word.
        """
        if char in 'Ее':
            return self._rules_for_e(word, char, char_index)
        elif char in 'Ёё':
            return self._rules_for_jo(word, char, char_index)
        elif char in 'ИиЙй':
            return self._rules_for_i(word, char, char_index)
        elif char in 'Хх':
            return self._rules_for_h(word, char, char_index)
        elif char in 'Ьь':
            return self._rules_for_soft(word, char, char_index)
        elif char in 'Сс':
            return self._rules_for_s(word, char, char_index)

    def _rules_for_s(self, word, char, char_index):
        """Checks rules for the cyr s character
            Returns: [string] -- Returns 'Ss/ss/S/s' based on the rules
        """
        char_to_return = ''
        if char_index > 0:
            if word[char_index-1] in self._vocals_rus:
                if len(word) == 2:
                    char_to_return = self._check_if_upper_and_return(
                        char, 'Ss')
                # To avoid keyerror use len(word[char_index+1:])
                elif len(word[char_index+1:]) > 0 and word[char_index+1] in self._vocals_rus:
                    char_to_return = self._check_if_upper_and_return(
                        char, 'Ss')
                elif word[-1] == char:
                    char_to_return = self._check_if_upper_and_return(
                        char, 'Ss')

        if char_to_return == '':
            char_to_return = self._chars_with_rules[char]

        return char_to_return

    def _rules_for_soft(self, word, char, char_index):
        """Checks rules for the cyr softening character
            Returns: [string] -- Returns 'J/j//' based on the rules
        """
        if len(word[char_index+1:]) > 0 and word[char_index+1] not in 'еЕёЁюЮяЯ' and word[char_index+1] in self._vocals_rus:
            char_to_return = self._check_if_upper_and_return(char, 'J')
        else:
            return self._chars_with_rules[char]

        return char_to_return

    def _rules_for_e(self, word, char, char_index):
        """Checks rules for the cyr character 'e'
            Returns: [string] -- Returns 'Je/je/E/e' based on the rules
        """
        if char_index == 0:
            char_to_return = self._check_if_upper_and_return(char, 'Je')
        elif word[char_index - 1] in self._vocals_rus or word[char_index - 1] in 'ЬьЪъ':
            char_to_return = self._check_if_upper_and_return(char, 'Je')
        else:
            char_to_return = self._chars_with_rules[char]

        return char_to_return

    def _rules_for_jo(self, word, char, char_index):
        """Checks rules for the cyr character 'jo'
            Returns: [string] -- Returns 'O/o/Jo/jo' based on the rules
        """
        char_to_return = ''
        if char_index != 0:
            if word[char_index-1] in 'ЖжЧчШшЩщ':
                char_to_return = self._check_if_upper_and_return(char, 'O')

        if char_to_return == '':
            char_to_return = self._chars_with_rules[char]

        return char_to_return

    def _rules_for_i(self, word, char, char_index):
        """Checks rules for the cyr character 'i'
        Returns: [string] -- Returns 'J/j/I/i' based on the rules
        """
        char_to_return = ''
        if len(word) > 1:
            if char_index == 0 and word[char_index + 1] in self._vocals_rus:
                char_to_return = self._check_if_upper_and_return(char, 'J')

        if char_to_return == '':
            char_to_return = self._chars_with_rules[char]

        return char_to_return

    def _rules_for_h(self, word, char, char_index):
        """Checks rules for the cyr character 'h'
        Returns: [string] -- Returns 'Hh/hh/H/h' based on the rules
        """
        char_to_return = ''
        if char_index > 0:
            if word[char_index-1] in self._vocals_rus:
                if len(word) == 2:
                    char_to_return = self._check_if_upper_and_return(
                        char, 'Hh')
                # To avoid keyerror use len(word[char_index+1:])
                elif len(word[char_index+1:]) > 0 and word[char_index+1] in self._vocals_rus:
                    char_to_return = self._check_if_upper_and_return(
                        char, 'Hh')
                elif word[-1] == char:
                    char_to_return = self._check_if_upper_and_return(
                        char, 'Hh')

        if char_to_return == '':
            char_to_return = self._chars_with_rules[char]

        return char_to_return

    @staticmethod
    def _check_if_upper_and_return(char_in_index, char):
        """Checks whether the character is supposed to be lower or upper case

        Arguments:
            char_in_index {string} -- [The value of the char index in the word]
            char {string} -- [The character to return, should be first letter uppercase, ex: 'Je']

        Returns:
            [string] -- [Upper or lower case version of the character]
        """
        if char_in_index.isupper():
            return char
        else:
            return char.lower()

    # Ugly constants too big for init method
    _vocals_est = ['i', 'ü', 'u', 'e', 'ö', 'õ', 'o', 'ä', 'a']
    _vocals_rus = ['а', 'э', 'ы', 'у', 'о', 'я', 'е', 'ё', 'ю', 'и']
    _translit_table = {
        'А': 'A', 'а': 'a',
        'Б': 'B', 'б': 'b',
        'В': 'V', 'в': 'v',
        'Г': 'G', 'г': 'g',
        'Д': 'D', 'д': 'd',
        'Ж': 'Ž', 'ж':  'ž',
        'З': 'Z', 'з': 'z',
        'К': 'K', 'к': 'k',
        'Л': 'L', 'л': 'l',
        'М': 'M', 'м': 'm',
        'Н': 'N', 'н': 'n',
        'О': 'O', 'о': 'o',
        'П': 'P', 'п': 'p',
        'Р': 'R', 'р': 'r',
        'Т': 'T', 'т': 't',
        'У': 'U', 'у': 'u',
        'Ф': 'F', 'ф': 'f',
        'Ц': 'Ts', 'ц':  'ts',
        'Ч': 'Tš', 'ч':  'tš',
        'Ш': 'Š', 'ш':  'š',
        'Щ': 'Štš', 'щ': 'štš',
        'Ы': 'õ', 'ы': 'õ',
        'Ъ': "", 'ъ': "",
        'Э': 'E', 'э': 'e',
        'Ю': 'Ju', 'ю': 'ju',
        'Я': 'Ja', 'я': 'ja'}
    _chars_with_rules = {
        'Е': 'E', 'е': 'e',
        'Ё': 'Jo', 'ё': 'jo',
        'И': 'I', 'и': 'i',
        'Й': 'I', 'й': 'i',
        'Х': 'H', 'х':  'h',
        'Ь': "", 'ь': "",
        'С': 'S', 'с': 's',
    }


if __name__ == '__main__':
    trans = Transliterate()
    transcribed = trans(['Дженни играет с мяц.', 'Яне говорит на телефоне.',
                         'Рассекречены планы выпуска дешевого iPhone Читать далее',
                         'FOR E: Сергей = Sergei, Петропавловск = Petropavlovsk; aga Егоров = Jegorov, Алексеев = Aleksejev, Мясоедов = Mjassojedov, Васильев = Vassiljev, Подъездов = Podjezdov',
                         'FOR JO: Орёл = Orjol, Пётр = Pjotr; aga Жёлтый = Žoltõi, Пугачёв = Pugatšov, Шёлков = Šolkov, Щёкино = Štšokino',
                         'FOR I: Исаев = Issajev, Филин =Filin; aga Иосиф = Jossif, Иовлев = Jovlev',
                         'FOR H: Хабаровск = Habarovsk, Мохнатый = Mohnatõi, Верхоянск = Verhojansk; aga Чехов = Tšehhov, Тихонов = Tihhonov, Мономах = Monomahh, Черных = Tšernõhh, Долгих = Dolgihh',
                         'FOR SOFT: Юрьевец = Jurjevets, Тотьма = Totma, Нинель = Ninel, aga Ильич = Iljitš, Почтальон = Potštaljon, also Иль',
                         'FOR S: Серов = Serov, Курск = Kursk; aga Писарев = Pissarev, Василий = Vassili, Денис = Deniss',
                         'FOR II: Новороссийск = Novorossiisk, Вий = Vii; aga Горький = Gorki, Чайковский =Tšaikovski'])
    for i in transcribed:
        print(i)
