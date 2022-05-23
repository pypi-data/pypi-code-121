import json
import os

from kolibri import settings as k
from kolibri.logger import get_logger
from kolibri.data.text.resources import resources
from pathlib import Path
logger = get_logger(__name__)

STOP_WORDS_CACHE = {}


stopwords = resources.get(str(Path('modules','stop-words'))).path

class Stopwords():

    def __init__(self):
        """
        :param with_additional_file: Allows to load LEFFF without the additional file. (Default: True)
        :type with_additional_file: bool
        :param load_only_pos: Allows to load LEFFF with only some pos tags: WordNet pos tags [a, r, n, v]. (Default: all)
        :type load_only_pos: list
        """
        #        data_file_path = os.path.dirname(os.path.realpath(__file__))

        self.stopwords_path = os.path.join(k.DATA_PATH,'modules', 'stop-words')
        if os.path.exists(self.stopwords_path):
            with open(os.path.join(self.stopwords_path, 'languages.json'), 'rb') as map_file:
                buffer = map_file.read()
                buffer = buffer.decode('ascii')
                self.LANGUAGE_MAPPING = json.loads(buffer)

            self.AVAILABLE_LANGUAGES = list(self.LANGUAGE_MAPPING.values())
        else:
            print("Could not find stopword file in :"+self.stopwords_path)

class StopWordError(Exception):
    pass


__sw = Stopwords()


def get_stop_words(language, cache=True, aggressive=False):
    """
    :type language: basestring
    :rtype: list
    """
    try:
        language = __sw.LANGUAGE_MAPPING[language]
    except KeyError:
        if language not in __sw.AVAILABLE_LANGUAGES:
            raise StopWordError('{0}" language is unavailable.'.format(
                language
            ))

    if cache and language in STOP_WORDS_CACHE:
        return STOP_WORDS_CACHE[language]
    language_name = language
    if aggressive:
        language_name + "-aggressive"
    language_filename = os.path.join(__sw.stopwords_path, language_name + '.txt')
    try:
        with open(language_filename, 'rb') as language_file:
            stop_words = [line.decode('utf-8').strip()
                          for line in language_file.readlines()]
    except IOError:
        raise StopWordError(
            '{0}" file is unreadable, check your installation.'.format(
                language_filename
            )
        )

    if cache:
        STOP_WORDS_CACHE[language] = stop_words

    return stop_words


if __name__ == "__main__":
    stp = get_stop_words('en')

    print(stp)
