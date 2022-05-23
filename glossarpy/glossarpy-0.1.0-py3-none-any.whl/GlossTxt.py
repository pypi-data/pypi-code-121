import re


class GlossTxt:
    '''Handles RST-specific output'''

    def underline_text(self, text:str, underlinechar:str = "-"):
        '''Underlines text, used to create a valid rst header or make txt prettier'''
        return [f"{text}\n", underlinechar * len(text) + "\n"]

    def rst_url(self, url:str, internal:bool = False):
        '''Generate an RST URL for further reading.
        If internal, assume this is an internal URL within Sphinx documentation
        Otherwise, assume this is a standard URL to an external webpage'''
        if internal:
            return f":doc:`{url} <{url}>`"
        else:
            return f"`<{url}>`_"

    def rst_bookmark(self):
        '''Generates an RST bookmark for the entry'''
        return f".. _dict {self.return_name(nospaces=False)}:"

    def rst_process_brackets(self, words:list):
        '''Turn [this] into an RST internal link, assuming the part being linked to
        has a bookmark created with rst_bookmark(). Expects words to be a list of
        strings, split upon spaces.'''
        words_processed = []
        multi_word_flag = False
        for word in words:
            if re.search("][a-zA-Z]+", word):
                print(f"""Warning: An entry will have an invalid internal link
                    due RST limitations. Put some sort of whitespace or punctuation before
                    any additional letters after the ending bracket. Problematic word: {word}""")

            # This is the beginning of an internal RST link
            elif word.startswith("["):
                word = word[1:]  # strip [
                if "]" in word:
                    multi_word_flag = False
                    word = word.replace("]", "`")
                    word = f":ref:`dict {word}"
                else:
                    multi_word_flag = True
                    word = f":ref:`dict {word}"

                words_processed.append(word)

            # This is a continuation of a previous word's RST link
            # will break on [Seven Br]idges] but that's not my problem
            elif multi_word_flag is True:

                if "]" in word:
                    multi_word_flag = False
                    word = word.replace("]", "`")
                    word = f"{word}"
                else:
                    word = f"{word}"

                words_processed.append(word)

            else:
                words_processed.append(word)

        return " ".join(words_processed)
