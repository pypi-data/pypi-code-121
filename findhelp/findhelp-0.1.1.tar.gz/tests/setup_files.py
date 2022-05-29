import os
import shutil
import __main__

TEMP_FOLDER_NAME = "__search_tests_dummy_folder__"
ROOT_PATH = os.path.join(os.path.dirname(__main__.__file__), TEMP_FOLDER_NAME)


PATH_TREE = {
    "1": "1.mp3",
    "2": "2.mp3",
    "2": "3.mp3",
    "4": "4.mp3",
    "5": "oñe",
    "6": "óne",
    "node_modules": {
        "node_inside1": {
        },
        "node_inside2": {
        },
        "node_inside3": {
        },
        "node_modules": {
            1: "dummy.txt",
            "folder": {
            }
        }
    },
    "one": {
    },
    "oné": {
    },
    "test": {
        "dir1": {
            "1": "one.txt",
            "2": "two.txt",
            "3": "three.txt"
        },
        "dir2": {
            "1": "one.md",
            "2": "two.pdf",
            "3": "three.doc"
        },
        "dir3": {
        }
    },
    "test1": {
        "1": "one.csv",
        "2": "onè.json",
        "3": "oné.csv",
        "4": "twò.txt",
        "5": "twó"
    },
    "test2": {
        "site-packages": {
            "site_inside1": {
                "1": "sp_one",
                "2": "sp_one.json",
                "3": "sp_two.csv",
                "4": "sp_three.txt",
                "5": "sp_four.pdf"
            },
            "site_inside2": {
            },
            "site_inside3": {
            },
            "1": "one",
            "2": "one.json",
            "3": "three.txt",
            "4": "two.csv",
        },
        "test01": {
            "1": "file1.ext",
            "2": "file2.mp3",
            "3": "file3.mp4",
            "4": "one.md",
        },
        "test02": {
            "1": "1.mpg",
            "2": "2.avi",
            "3": "3.mkv",
        },
        "test03": {
        }
    },
    "test3": {
    },
    "trés": {
    },
    "two": {
    }
}


def create_base_folder():
    try:
        if os.path.exists(ROOT_PATH):
            shutil.rmtree(ROOT_PATH)
        os.mkdir(ROOT_PATH)
    except Exception as e:
        print(e)


def create_element(path, tree: dict):
    for key, value in tree.items():
        if isinstance(value, dict):
            os.makedirs(os.path.join(path, key))
            create_element(os.path.join(path, key), value)
        else:
            with open(os.path.join(path, value), "w") as f:
                pass


def create_tree(tree_object):
    create_element(ROOT_PATH, tree_object)


def setup_tests():
    create_base_folder()
    create_tree(PATH_TREE)
