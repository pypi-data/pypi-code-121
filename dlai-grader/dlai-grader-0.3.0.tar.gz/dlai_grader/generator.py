import os
from .templates import load_templates


def write_file(filename, template):
    with open(filename, "w") as f:
        f.write(template)


def init():

    template_dict = load_templates()
    write_file("./Dockerfile", template_dict.get("dockerfile"))
    write_file("./grader.py", template_dict.get("grader_py"))
    write_file("./Makefile", template_dict.get("makefile"))
    write_file("./.conf", template_dict.get("conf"))
    write_file("./entry.py", "")
    write_file("./requirements.txt", "dlai-grader")
    os.makedirs("data")
    os.makedirs("learner")
    os.makedirs("mount")
    os.makedirs("solution")
    os.makedirs("submission")
