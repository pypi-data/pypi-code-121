import os
import re

def remove_files(filepaths):
    for filepath in filepaths:
        if os.path.isfile(filepath):
            os.remove(filepath)


def get_generic_language(language):
    return re.sub(r'(-[r]|-)', '_', language)
