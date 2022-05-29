import os
import shutil
import __main__

TEMP_FOLDER_NAME = "__search_tests_dummy_folder__"
ROOT_PATH = os.path.join(os.path.dirname(__main__.__file__), TEMP_FOLDER_NAME)


def drop_test_folder():
    try:
        if os.path.exists(ROOT_PATH):
            shutil.rmtree(ROOT_PATH)
    except Exception as e:
        print(e)


def tear_down_tests():
    drop_test_folder()
