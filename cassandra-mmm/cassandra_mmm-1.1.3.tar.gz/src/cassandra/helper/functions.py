import os

def help_clean_and_format():
    path = os.path.join(os.path.dirname(__file__), "clean_and_format.txt")
    with open(path) as f:
        file_contents = f.read()
        print(file_contents)

def help_import():
    path = os.path.join(os.path.dirname(__file__), "import.txt")
    with open(path) as f:
        file_contents = f.read()
        print(file_contents)

def help_pivot():
    path = os.path.join(os.path.dirname(__file__), "pivot.txt")
    with open(path) as f:
        file_contents = f.read()
        print(file_contents)

def help_nevergrad():
    path = os.path.join(os.path.dirname(__file__), "nevergrad.txt")
    with open(path) as f:
        file_contents = f.read()
        print(file_contents)