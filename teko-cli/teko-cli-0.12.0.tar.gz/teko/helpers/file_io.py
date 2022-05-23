import codecs
import os


def remove_if_exists(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)


def write_file(file_path: str, content: str):
    with codecs.open(file_path, 'a', 'utf-8') as test_cycle:
        test_cycle.write(content)
        test_cycle.close()
